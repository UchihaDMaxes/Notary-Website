"""Scanner endpoints: list devices and acquire a page."""
import base64
import os

from flask import Blueprint, jsonify, request
from flask_login import login_required

import scanner

scan_bp = Blueprint("scan", __name__, url_prefix="/scan")


@scan_bp.get("/devices")
@login_required
def devices():
    """Return scanner availability and the list of attached scanners."""
    available = scanner.available()
    found = scanner.list_devices() if available else []
    return jsonify({
        "available": available,
        "devices": found,
        "count": len(found),
    })


@scan_bp.post("/capture")
@login_required
def capture():
    """Acquire one page and return it as a data URL for preview."""
    payload = request.get_json(silent=True) or {}
    try:
        dpi = int(payload.get("dpi") or 200)
    except (TypeError, ValueError):
        dpi = 200
    dpi = max(75, min(dpi, 1200))
    color = bool(payload.get("color", True))
    device_id = payload.get("device") or None

    try:
        path = scanner.scan(device_id=device_id, dpi=dpi, color=color)
    except RuntimeError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - defensive
        return jsonify({"ok": False, "error": f"Scan failed: {exc}"}), 500

    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

    if not raw:
        return jsonify({"ok": False, "error": "The scanner returned an empty image."}), 400

    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    data_url = f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"
    return jsonify({"ok": True, "image": data_url, "bytes": len(raw)})

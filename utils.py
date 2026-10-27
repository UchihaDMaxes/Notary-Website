"""Shared helpers: language handling, file uploads, permissions."""
import os
import uuid

from flask import session, request, abort, current_app, send_from_directory
from flask_login import current_user
from werkzeug.utils import secure_filename

from translations import DEFAULT_LANG, LANGUAGES, translate


def get_lang():
    """Resolve the active language: user pref -> session -> default."""
    if current_user.is_authenticated and getattr(current_user, "language", None) in LANGUAGES:
        return current_user.language
    lang = session.get("lang")
    if lang in LANGUAGES:
        return lang
    # honour an explicit ?lang= switch
    q = request.args.get("lang")
    if q in LANGUAGES:
        session["lang"] = q
        return q
    return DEFAULT_LANG


def t(key, lang=None):
    """Translate a key using the active language."""
    return translate(key, lang or get_lang())


def register_template_helpers(app):
    """Expose `t`, `lang`, `LANGUAGES` and record-type labels to all templates."""
    from translations import type_label, IIB_TYPES, HESHIIS_TYPES

    @app.context_processor
    def inject_helpers():
        lang = get_lang()
        return {
            "t": t,
            "lang": lang,
            "LANGUAGES": LANGUAGES,
            "type_label": lambda v: type_label(v, lang),
            "IIB_TYPES": IIB_TYPES,
            "HESHIIS_TYPES": HESHIIS_TYPES,
        }


def allowed_file(filename):
    return (
        "."
        in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_upload(file):
    """Persist an uploaded file to disk under a random name.

    Returns (stored_name, original_name, content_type, size) or None when the
    file is empty / not allowed.
    """
    if not file or not file.filename:
        return None
    original = secure_filename(file.filename)
    if not original or not allowed_file(original):
        return None
    ext = original.rsplit(".", 1)[1].lower()
    stored = f"{uuid.uuid4().hex}.{ext}"
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, stored))
    size = os.path.getsize(os.path.join(folder, stored))
    content_type = file.mimetype or "application/octet-stream"
    return stored, original, content_type, size


def save_data_url(data_url, prefix="scan"):
    """Persist a base64 ``data:image/...`` URL as a file on disk.

    Returns (stored_name, original_name, content_type, size) or None.
    """
    import base64
    import re
    from datetime import datetime

    if not isinstance(data_url, str):
        return None
    match = re.match(r"^data:(image/[a-zA-Z0-9.+-]+);base64,(.+)$", data_url.strip(), re.S)
    if not match:
        return None
    mime = match.group(1).lower()
    try:
        raw = base64.b64decode(match.group(2), validate=False)
    except Exception:
        return None
    if not raw or len(raw) > 32 * 1024 * 1024:
        return None

    ext = {
        "image/jpeg": "jpg", "image/jpg": "jpg", "image/png": "png",
        "image/webp": "webp", "image/gif": "gif", "image/bmp": "bmp",
        "image/tiff": "tiff",
    }.get(mime, "png")

    stored = f"{uuid.uuid4().hex}.{ext}"
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, stored), "wb") as fh:
        fh.write(raw)

    original = f"{prefix}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.{ext}"
    return stored, original, mime, len(raw)


def attach_documents(record, files=None, scanned_json=None):
    """Attach uploaded files and/or scanned (data-URL) images to a record.

    `record` must be an Iib or Heshiis instance (anything with `.documents`).
    Scanned images arrive as a JSON array of data URLs in the `scanned` field.
    """
    import json
    from models import Document

    created = []

    for file in files or []:
        saved = save_upload(file)
        if saved:
            stored, original, content_type, size = saved
            doc = Document(filename=stored, original_name=original,
                           content_type=content_type, size=size)
            record.documents.append(doc)
            created.append(doc)

    if scanned_json:
        try:
            items = json.loads(scanned_json)
        except (ValueError, TypeError):
            items = []
        if not isinstance(items, list):
            items = []
        for index, item in enumerate(items):
            saved = save_data_url(item, prefix=f"scan-{index + 1}")
            if saved:
                stored, original, content_type, size = saved
                doc = Document(filename=stored, original_name=original,
                               content_type=content_type, size=size)
                record.documents.append(doc)
                created.append(doc)

    return created


def document_response(document):
    """Serve a stored document, setting the download filename."""
    folder = current_app.config["UPLOAD_FOLDER"]
    # Inline-view images/PDFs; force download otherwise.
    as_attachment = not document.is_image
    return send_from_directory(
        folder,
        document.filename,
        as_attachment=as_attachment,
        download_name=document.original_name,
        max_age=0,
    )


def admin_required(view):
    """Decorator: abort with 403 unless the current user is an active admin."""

    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped

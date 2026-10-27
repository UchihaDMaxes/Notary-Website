"""Direct scanner access for the local notary app (Windows / WIA).

Uses Windows Image Acquisition (WIA) through `pywin32`. Everything degrades
gracefully: if pywin32 is missing or no scanner is attached, the web UI falls
back to file import or the browser camera.

This module never raises on import — call `available()` first.
"""
from __future__ import annotations

import os
import tempfile
import threading
import uuid

# Serialise scans: most scanners cannot handle concurrent jobs.
_scan_lock = threading.Lock()

# WIA image format GUIDs
_FMT_JPEG = "{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}"
_FMT_PNG = "{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}"

# WIA property ids
_PROP_INTENT = 6147      # 1 = color, 2 = grayscale, 4 = text/BW
_PROP_DPI_X = 6148
_PROP_DPI_Y = 6149

# WIA device types
_DEVICE_SCANNER = 1


def available() -> bool:
    """True when pywin32 + COM are importable on this machine."""
    try:
        import pythoncom  # noqa: F401
        import win32com.client  # noqa: F401
        return True
    except Exception:
        return False


def list_devices() -> list[dict]:
    """Return installed WIA scanners as ``[{"id", "name"}]``."""
    if not available():
        return []

    import gc

    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    manager = None
    try:
        manager = win32com.client.Dispatch("WIA.DeviceManager")
        devices = []
        for info in manager.DeviceInfos:
            try:
                if info.Type != _DEVICE_SCANNER:
                    continue
            except Exception:
                continue
            name = _read_prop(info.Properties, "Name") or info.DeviceID
            devices.append({"id": str(info.DeviceID), "name": str(name)})
        return devices
    except Exception:
        return []
    finally:
        # Release COM references *before* uninitialising, otherwise pywin32
        # prints "Win32 exception occurred releasing IUnknown" noise.
        manager = None
        gc.collect()
        pythoncom.CoUninitialize()


def scan(device_id: str | None = None, dpi: int = 200, color: bool = True,
         fmt: str = "jpeg") -> str:
    """Acquire a single page and return the path to a temporary image file.

    Raises RuntimeError with a user-facing message when it cannot scan.
    """
    if not available():
        raise RuntimeError("Scanner support is not installed (pywin32 missing).")

    import gc

    import pythoncom
    import win32com.client

    with _scan_lock:
        pythoncom.CoInitialize()
        manager = target = device = item = image = None
        try:
            manager = win32com.client.Dispatch("WIA.DeviceManager")

            target = None
            for info in manager.DeviceInfos:
                try:
                    if info.Type != _DEVICE_SCANNER:
                        continue
                except Exception:
                    continue
                if device_id is None or info.DeviceID == device_id:
                    target = info
                    break

            if target is None:
                raise RuntimeError("No scanner detected.")

            device = target.Connect()
            item = device.Items[1]

            _write_prop(item.Properties, _PROP_INTENT, 1 if color else 2)
            _write_prop(item.Properties, _PROP_DPI_X, int(dpi))
            _write_prop(item.Properties, _PROP_DPI_Y, int(dpi))

            guid = _FMT_PNG if fmt == "png" else _FMT_JPEG
            image = item.Transfer(guid)

            ext = "png" if fmt == "png" else "jpg"
            path = os.path.join(tempfile.gettempdir(), f"scan_{uuid.uuid4().hex}.{ext}")
            image.SaveFile(path)
            return path
        except Exception as exc:  # turn COM errors into friendly messages
            raise RuntimeError(f"Scan failed: {exc}") from exc
        finally:
            # Drop COM references first so pywin32 does not warn on release.
            image = item = device = target = manager = None
            gc.collect()
            pythoncom.CoUninitialize()


def _read_prop(props, name):
    try:
        return props.Item(name).Value
    except Exception:
        return None


def _write_prop(props, prop_id, value):
    try:
        props.Item(prop_id).Value = value
    except Exception:
        # Not all devices expose every property; ignore unsupported ones.
        pass

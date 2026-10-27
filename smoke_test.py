"""Smoke test: build the app, seed the DB, and exercise key routes."""
import os
import sys
import tempfile

# Use a throwaway DB + upload dir so we never touch real data.
import config


class TestConfig(config.Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")
    UPLOAD_FOLDER = tempfile.mkdtemp()
    WTF_CSRF_ENABLED = False


from app import create_app  # noqa: E402
from models import db, User, Iib, Heshiis  # noqa: E402

app = create_app(TestConfig)

failures = []


def check(name, cond, extra=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name} {extra}")
    if not cond:
        failures.append(name)


client = app.test_client()

# --- Auth: login page renders ---
r = client.get("/login")
check("GET /login -> 200", r.status_code == 200, f"({r.status_code})")

# --- Auth: bad login rejected ---
r = client.post("/login", data={"username": "admin", "password": "wrong"}, follow_redirects=True)
check("Bad login rejected", b"error" in r.data or r.request.path == "/login")

# --- Auth: good login redirects to dashboard ---
r = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)
check("Good login -> dashboard", r.status_code == 200 and b"dashboard" in r.data.lower() or r.request.path == "/", f"({r.status_code}, path={r.request.path})")

# --- Dashboard ---
r = client.get("/")
check("GET / dashboard", r.status_code == 200, f"({r.status_code})")

# --- Create an IIB record ---
r = client.post("/iib/new", data={
    "date": "2026-01-15", "faahfaahin": "IIB DHUL", "cabir": "100x100",
    "qiime": "15000.50", "kuyaalla": "Mogadishu",
    "iibiye": "Ali", "number1": "615000001",
    "iibsade": "Ahmed", "number2": "615000002",
    "damiin": "Omar", "number3": "615000003", "notes": "test note",
}, follow_redirects=True)
check("POST /iib/new", r.status_code == 200)

with app.app_context():
    check("IIB row saved", Iib.query.count() == 1, f"(count={Iib.query.count()})")

# --- Create a HESHIIS record ---
r = client.post("/heshiis/new", data={
    "date": "2026-02-20", "faahfaahin": "HESHIIS KIRO", "qiime": "800",
    "kireeye": "Fatima", "number1": "615000004",
    "kireyste": "Sagal", "number2": "615000005", "goob": "Hodan",
}, follow_redirects=True)
check("POST /heshiis/new", r.status_code == 200)

with app.app_context():
    check("HESHIIS row saved", Heshiis.query.count() == 1)

# --- Lists render ---
for path in ["/iib/", "/heshiis/"]:
    r = client.get(path)
    check(f"GET {path}", r.status_code == 200, f"({r.status_code})")

# --- Detail pages ---
with app.app_context():
    iid = Iib.query.first().id
    hid = Heshiis.query.first().id
for path in [f"/iib/{iid}", f"/iib/{iid}/edit", f"/heshiis/{hid}", f"/heshiis/{hid}/edit"]:
    r = client.get(path)
    check(f"GET {path}", r.status_code == 200, f"({r.status_code})")

# --- Search finds the records ---
r = client.get("/search?q=Ali")
check("Search hits (Ali)", r.status_code == 200 and b"Ali" in r.data)
r = client.get("/search?q=Fatima")
check("Search hits (Fatima)", r.status_code == 200 and b"Fatima" in r.data)

# --- Language toggle ---
r = client.get("/lang/en", follow_redirects=True)
check("Language toggle -> EN", r.status_code == 200)

# --- Users admin page ---
r = client.get("/users/")
check("GET /users/ (admin)", r.status_code == 200, f"({r.status_code})")

# --- Settings ---
r = client.get("/settings")
check("GET /settings", r.status_code == 200, f"({r.status_code})")

# --- Document upload round-trip ---
import io  # noqa: E402

png = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
       b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
       b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
r = client.post("/iib/new", data={
    "date": "2026-03-01", "faahfaahin": "IIB GURI", "qiime": "5000",
    "iibiye": "Doc Tester",
    "documents": (io.BytesIO(png), "scan.png"),
}, content_type="multipart/form-data", follow_redirects=True)
check("POST /iib/new with upload", r.status_code == 200)

with app.app_context():
    from models import Document
    dcount = Document.query.count()
    check("Document row saved", dcount == 1, f"(count={dcount})")
    did = Document.query.first().id
    upload_iid = Iib.query.order_by(Iib.id.desc()).first().id
r = client.get(f"/iib/doc/{did}")
check("Document served", r.status_code == 200, f"({r.status_code})")

# --- Document picker (import OR scan) is rendered on the forms ---
for path in ["/iib/new", f"/iib/{upload_iid}", "/heshiis/new", f"/heshiis/{hid}"]:
    r = client.get(path)
    has_picker = b"data-docpicker" in r.data and b'data-scan-modal' in r.data
    check(f"Picker rendered on {path}", r.status_code == 200 and has_picker,
          f"({r.status_code}, picker={has_picker})")

# --- Scanner endpoints ---
r = client.get("/scan/devices")
devices_payload = r.get_json() if r.is_json else None
check("GET /scan/devices -> JSON",
      r.status_code == 200 and isinstance(devices_payload, dict)
      and "available" in devices_payload and "devices" in devices_payload,
      f"({r.status_code}, available={devices_payload and devices_payload.get('available')})")

r = client.post("/scan/capture", json={})
capture_payload = r.get_json() if r.is_json else None
if devices_payload and not devices_payload.get("devices"):
    # No scanner hardware in this environment: must fail gracefully, not crash.
    check("POST /scan/capture degrades gracefully (no hardware)",
          r.status_code == 400 and capture_payload is not None
          and capture_payload.get("ok") is False and capture_payload.get("error"),
          f"({r.status_code})")
else:
    check("POST /scan/capture responds", r.status_code in (200, 400),
          f"({r.status_code})")

# --- Attach scanned pages (data URLs) to an existing sale ---
import base64  # noqa: E402
import json  # noqa: E402

data_url = "data:image/png;base64," + base64.b64encode(png).decode("ascii")
with app.app_context():
    before = Document.query.filter_by(iib_id=upload_iid).count()
r = client.post(f"/iib/{upload_iid}/documents",
                data={"scanned": json.dumps([data_url, data_url])},
                follow_redirects=True)
with app.app_context():
    after = Document.query.filter_by(iib_id=upload_iid).count()
check("POST /iib/<id>/documents with scanned pages",
      r.status_code == 200 and after == before + 2, f"({before} -> {after})")

# --- Attach an imported file to an existing contract ---
with app.app_context():
    h_before = Document.query.filter_by(heshiis_id=hid).count()
r = client.post(f"/heshiis/{hid}/documents",
                data={"documents": (io.BytesIO(png), "page.png")},
                content_type="multipart/form-data", follow_redirects=True)
with app.app_context():
    h_after = Document.query.filter_by(heshiis_id=hid).count()
check("POST /heshiis/<id>/documents with file",
      r.status_code == 200 and h_after == h_before + 1, f"({h_before} -> {h_after})")

# --- Bad payloads must not create documents ---
r = client.post(f"/iib/{upload_iid}/documents",
                data={"scanned": "not-json"}, follow_redirects=True)
check("Malformed scanned payload ignored", r.status_code == 200)
r = client.post("/iib/9999/documents", data={"scanned": "[]"}, follow_redirects=False)
check("Attach to missing record -> 404", r.status_code == 404, f"({r.status_code})")

# --- Logout ---
r = client.get("/logout", follow_redirects=True)
check("Logout -> login", r.request.path == "/login")

# --- Protected route requires auth ---
r = client.get("/", follow_redirects=False)
check("Unauth / redirects to login", r.status_code == 302 and "/login" in r.headers.get("Location", ""))

print()
if failures:
    print(f"!!! {len(failures)} FAILED: {failures}")
    sys.exit(1)
print("ALL SMOKE TESTS PASSED")

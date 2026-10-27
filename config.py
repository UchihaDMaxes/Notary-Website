import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Optional data directory. Keep the database and uploads together on hosts that
# provide a persistent disk (e.g. DATA_DIR=/var/data on Render, or a folder in
# your home directory on PythonAnywhere). Defaults to the project folder.
DATA_DIR = os.path.abspath(os.environ.get("DATA_DIR") or basedir)


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-change-me-in-production"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "sqlite:///" + os.path.join(DATA_DIR, "notary.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploaded documents are stored on disk (not as BLOBs in the DB).
    UPLOAD_FOLDER = os.path.abspath(
        os.environ.get("UPLOAD_FOLDER") or os.path.join(DATA_DIR, "uploads")
    )
    # 64 MB per request: scanned pages arrive base64-encoded (≈33% overhead),
    # and one record may carry several pages.
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024
    # Werkzeug ≥ 3.1 caps non-file form fields (the scanned-pages JSON) at
    # 500 KB by default; raise it so multi-page scans are accepted.
    MAX_FORM_MEMORY_SIZE = 64 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf"}

    # Items shown per page in list views.
    RECORDS_PER_PAGE = 12

    # Cookies: keep the session on the same site, and allow forcing HTTPS-only
    # cookies once the site is served over TLS (SESSION_COOKIE_SECURE=1).
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"

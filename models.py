"""SQLAlchemy models for the notary web application."""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from translations import DEFAULT_LANG, IIB_TYPES, HESHIIS_TYPES  # noqa: F401  (re-exported for convenience)

# db is created in app.py and imported by blueprints to avoid a circular import.
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="staff")  # admin | staff
    active = db.Column(db.Boolean, nullable=False, default=True)
    language = db.Column(db.String(2), nullable=False, default=DEFAULT_LANG)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def role_label_key(self):
        return "admin" if self.role == "admin" else "staff"


class Document(db.Model):
    """An uploaded file attached to a sale or contract record."""

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)        # stored name on disk
    original_name = db.Column(db.String(255), nullable=False)   # name shown to the user
    content_type = db.Column(db.String(100), nullable=False, default="application/octet-stream")
    size = db.Column(db.Integer, nullable=False, default=0)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    iib_id = db.Column(db.Integer, db.ForeignKey("iib.id", ondelete="CASCADE"), nullable=True)
    heshiis_id = db.Column(db.Integer, db.ForeignKey("heshiis.id", ondelete="CASCADE"), nullable=True)

    @property
    def is_image(self):
        return (self.content_type or "").startswith("image/")

    @property
    def human_size(self):
        size = self.size or 0
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"


class Iib(db.Model):
    """A sale record (Iib)."""

    __tablename__ = "iib"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    faahfaahin = db.Column(db.String(120))
    cabir = db.Column(db.String(120))
    qiime = db.Column(db.Float)
    kuyaalla = db.Column(db.String(200))

    iibiye = db.Column(db.String(120))
    number1 = db.Column(db.String(40))
    iibsade = db.Column(db.String(120))
    number2 = db.Column(db.String(40))
    damiin = db.Column(db.String(120))
    number3 = db.Column(db.String(40))

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    creator = db.relationship("User", backref="iib_records")
    documents = db.relationship(
        "Document",
        backref="iib",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="Document.uploaded_at.desc()",
    )


class Heshiis(db.Model):
    """A contract record (Heshiis)."""

    __tablename__ = "heshiis"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    faahfaahin = db.Column(db.String(120))
    qiime = db.Column(db.Float)

    kireeye = db.Column(db.String(120))
    number1 = db.Column(db.String(40))
    kireyste = db.Column(db.String(120))
    number2 = db.Column(db.String(40))
    goob = db.Column(db.String(200))

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    creator = db.relationship("User", backref="heshiis_records")
    documents = db.relationship(
        "Document",
        backref="heshiis",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="Document.uploaded_at.desc()",
    )

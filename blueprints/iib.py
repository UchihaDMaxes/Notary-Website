"""Sales (Iib) registry: list, create, view, edit, delete + document serving."""
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    current_app,
)
from flask_login import login_required, current_user

from models import db, Iib, Document
from utils import t, attach_documents, document_response
from translations import IIB_TYPES

iib_bp = Blueprint("iib", __name__, url_prefix="/iib")


def _parse_form(form):
    """Build an Iib record dict from submitted form data."""
    def num(key):
        raw = (form.get(key) or "").strip()
        return raw or None

    def money(key):
        raw = (form.get(key) or "").strip().replace(",", "")
        try:
            return float(raw) if raw else None
        except ValueError:
            return None

    date_raw = form.get("date") or ""
    date_obj = None
    if date_raw:
        try:
            date_obj = datetime.strptime(date_raw, "%Y-%m-%d").date()
        except ValueError:
            date_obj = None

    return {
        "date": date_obj,
        "faahfaahin": (form.get("faahfaahin") or "").strip() or None,
        "cabir": (form.get("cabir") or "").strip() or None,
        "qiime": money("qiime"),
        "kuyaalla": (form.get("kuyaalla") or "").strip() or None,
        "iibiye": (form.get("iibiye") or "").strip() or None,
        "number1": num("number1"),
        "iibsade": (form.get("iibsade") or "").strip() or None,
        "number2": num("number2"),
        "damiin": (form.get("damiin") or "").strip() or None,
        "number3": num("number3"),
        "notes": (form.get("notes") or "").strip() or None,
    }


@iib_bp.route("/")
@login_required
def list():
    page = request.args.get("page", 1, type=int)
    q = (request.args.get("q") or "").strip()
    ftype = (request.args.get("type") or "").strip()

    query = Iib.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Iib.iibiye.ilike(like),
                Iib.iibsade.ilike(like),
                Iib.damiin.ilike(like),
                Iib.kuyaalla.ilike(like),
                Iib.faahfaahin.ilike(like),
            )
        )
    if ftype:
        query = query.filter_by(faahfaahin=ftype)

    pagination = query.order_by(Iib.created_at.desc()).paginate(
        page=page, per_page=current_app.config["RECORDS_PER_PAGE"], error_out=False
    )
    return render_template(
        "iib/list.html",
        pagination=pagination,
        records=pagination.items,
        q=q,
        ftype=ftype,
    )


@iib_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        data = _parse_form(request.form)
        record = Iib(**data, created_by=current_user.id)
        attach_documents(record, request.files.getlist("documents"), request.form.get("scanned"))
        db.session.add(record)
        db.session.commit()
        flash(t("saved"), "success")
        return redirect(url_for("iib.detail", record_id=record.id))

    return render_template("iib/form.html", record=None)


@iib_bp.route("/<int:record_id>")
@login_required
def detail(record_id):
    record = db.session.get(Iib, record_id) or abort(404)
    return render_template("iib/detail.html", record=record)


@iib_bp.route("/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
def edit(record_id):
    record = db.session.get(Iib, record_id) or abort(404)
    if request.method == "POST":
        data = _parse_form(request.form)
        for key, value in data.items():
            setattr(record, key, value)
        attach_documents(record, request.files.getlist("documents"), request.form.get("scanned"))
        db.session.commit()
        flash(t("updated"), "success")
        return redirect(url_for("iib.detail", record_id=record.id))

    return render_template("iib/form.html", record=record)


@iib_bp.route("/<int:record_id>/delete", methods=["POST"])
@login_required
def delete(record_id):
    record = db.session.get(Iib, record_id) or abort(404)
    # remove stored files from disk
    for doc in record.documents:
        try:
            import os

            os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], doc.filename))
        except OSError:
            pass
    db.session.delete(record)
    db.session.commit()
    flash(t("deleted"), "success")
    return redirect(url_for("iib.list"))


@iib_bp.route("/<int:record_id>/documents", methods=["POST"])
@login_required
def attach(record_id):
    """Attach newly imported or scanned documents to an existing sale."""
    record = db.session.get(Iib, record_id) or abort(404)
    created = attach_documents(
        record, request.files.getlist("documents"), request.form.get("scanned")
    )
    db.session.commit()
    if created:
        flash(t("saved"), "success")
    return redirect(url_for("iib.detail", record_id=record.id))


@iib_bp.route("/doc/<int:doc_id>")
@login_required
def document(doc_id):
    doc = db.session.get(Document, doc_id) or abort(404)
    if not doc.iib_id:
        abort(404)
    return document_response(doc)


@iib_bp.route("/doc/<int:doc_id>/delete", methods=["POST"])
@login_required
def document_delete(doc_id):
    doc = db.session.get(Document, doc_id) or abort(404)
    record_id = doc.iib_id
    if not record_id:
        abort(404)
    try:
        import os

        os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], doc.filename))
    except OSError:
        pass
    db.session.delete(doc)
    db.session.commit()
    flash(t("deleted"), "success")
    return redirect(url_for("iib.detail", record_id=record_id))

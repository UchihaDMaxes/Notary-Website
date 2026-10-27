"""Contracts (Heshiis) registry: list, create, view, edit, delete."""
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

from models import db, Heshiis, Document
from utils import t, attach_documents, document_response

heshiis_bp = Blueprint("heshiis", __name__, url_prefix="/heshiis")


def _parse_form(form):
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
        "qiime": money("qiime"),
        "kireeye": (form.get("kireeye") or "").strip() or None,
        "number1": num("number1"),
        "kireyste": (form.get("kireyste") or "").strip() or None,
        "number2": num("number2"),
        "goob": (form.get("goob") or "").strip() or None,
        "notes": (form.get("notes") or "").strip() or None,
    }


@heshiis_bp.route("/")
@login_required
def list():
    page = request.args.get("page", 1, type=int)
    q = (request.args.get("q") or "").strip()
    ftype = (request.args.get("type") or "").strip()

    query = Heshiis.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Heshiis.kireeye.ilike(like),
                Heshiis.kireyste.ilike(like),
                Heshiis.goob.ilike(like),
                Heshiis.faahfaahin.ilike(like),
            )
        )
    if ftype:
        query = query.filter_by(faahfaahin=ftype)

    pagination = query.order_by(Heshiis.created_at.desc()).paginate(
        page=page, per_page=current_app.config["RECORDS_PER_PAGE"], error_out=False
    )
    return render_template(
        "heshiis/list.html",
        pagination=pagination,
        records=pagination.items,
        q=q,
        ftype=ftype,
    )


@heshiis_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        data = _parse_form(request.form)
        record = Heshiis(**data, created_by=current_user.id)
        attach_documents(record, request.files.getlist("documents"), request.form.get("scanned"))
        db.session.add(record)
        db.session.commit()
        flash(t("saved"), "success")
        return redirect(url_for("heshiis.detail", record_id=record.id))

    return render_template("heshiis/form.html", record=None)


@heshiis_bp.route("/<int:record_id>")
@login_required
def detail(record_id):
    record = db.session.get(Heshiis, record_id) or abort(404)
    return render_template("heshiis/detail.html", record=record)


@heshiis_bp.route("/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
def edit(record_id):
    record = db.session.get(Heshiis, record_id) or abort(404)
    if request.method == "POST":
        data = _parse_form(request.form)
        for key, value in data.items():
            setattr(record, key, value)
        attach_documents(record, request.files.getlist("documents"), request.form.get("scanned"))
        db.session.commit()
        flash(t("updated"), "success")
        return redirect(url_for("heshiis.detail", record_id=record.id))

    return render_template("heshiis/form.html", record=record)


@heshiis_bp.route("/<int:record_id>/delete", methods=["POST"])
@login_required
def delete(record_id):
    record = db.session.get(Heshiis, record_id) or abort(404)
    import os

    for doc in record.documents:
        try:
            os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], doc.filename))
        except OSError:
            pass
    db.session.delete(record)
    db.session.commit()
    flash(t("deleted"), "success")
    return redirect(url_for("heshiis.list"))


@heshiis_bp.route("/<int:record_id>/documents", methods=["POST"])
@login_required
def attach(record_id):
    """Attach newly imported or scanned documents to an existing contract."""
    record = db.session.get(Heshiis, record_id) or abort(404)
    created = attach_documents(
        record, request.files.getlist("documents"), request.form.get("scanned")
    )
    db.session.commit()
    if created:
        flash(t("saved"), "success")
    return redirect(url_for("heshiis.detail", record_id=record.id))


@heshiis_bp.route("/doc/<int:doc_id>")
@login_required
def document(doc_id):
    doc = db.session.get(Document, doc_id) or abort(404)
    if not doc.heshiis_id:
        abort(404)
    return document_response(doc)


@heshiis_bp.route("/doc/<int:doc_id>/delete", methods=["POST"])
@login_required
def document_delete(doc_id):
    doc = db.session.get(Document, doc_id) or abort(404)
    record_id = doc.heshiis_id
    if not record_id:
        abort(404)
    import os

    try:
        os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], doc.filename))
    except OSError:
        pass
    db.session.delete(doc)
    db.session.commit()
    flash(t("deleted"), "success")
    return redirect(url_for("heshiis.detail", record_id=record_id))

"""Dashboard, global search, language switch and profile settings."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user

from models import db, Iib, Heshiis, Document, User
from utils import t, get_lang
from translations import LANGUAGES

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    iib_count = Iib.query.count()
    heshiis_count = Heshiis.query.count()
    doc_count = Document.query.count()

    recent_iib = Iib.query.order_by(Iib.created_at.desc()).limit(6).all()
    recent_heshiis = Heshiis.query.order_by(Heshiis.created_at.desc()).limit(6).all()

    stats = [
        {"label": t("total_iib"), "value": iib_count, "accent": "amber", "icon": "iib"},
        {"label": t("total_heshiis"), "value": heshiis_count, "accent": "blue", "icon": "heshiis"},
        {"label": t("total_records"), "value": iib_count + heshiis_count, "accent": "green", "icon": "total"},
        {"label": t("total_documents"), "value": doc_count, "accent": "purple", "icon": "doc"},
    ]

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_iib=recent_iib,
        recent_heshiis=recent_heshiis,
    )


@main_bp.route("/lang/<code>")
def set_lang(code):
    """Toggle UI language for guests (members' choice is saved to their profile)."""
    if code not in LANGUAGES:
        return redirect(url_for("main.dashboard"))
    session["lang"] = code
    if current_user.is_authenticated:
        current_user.language = code
        db.session.commit()
    return redirect(request.referrer or url_for("main.dashboard"))


@main_bp.route("/search")
@login_required
def search():
    q = (request.args.get("q") or "").strip()
    iib_results, heshiis_results = [], []

    if q:
        like = f"%{q}%"
        iib_results = (
            Iib.query.filter(
                db.or_(
                    Iib.iibiye.ilike(like),
                    Iib.iibsade.ilike(like),
                    Iib.damiin.ilike(like),
                    Iib.kuyaalla.ilike(like),
                    Iib.number1.ilike(like),
                    Iib.number2.ilike(like),
                    Iib.number3.ilike(like),
                    Iib.faahfaahin.ilike(like),
                )
            )
            .order_by(Iib.created_at.desc())
            .limit(50)
            .all()
        )
        heshiis_results = (
            Heshiis.query.filter(
                db.or_(
                    Heshiis.kireeye.ilike(like),
                    Heshiis.kireyste.ilike(like),
                    Heshiis.goob.ilike(like),
                    Heshiis.number1.ilike(like),
                    Heshiis.number2.ilike(like),
                    Heshiis.faahfaahin.ilike(like),
                )
            )
            .order_by(Heshiis.created_at.desc())
            .limit(50)
            .all()
        )

    total = len(iib_results) + len(heshiis_results)
    return render_template(
        "search.html",
        q=q,
        iib_results=iib_results,
        heshiis_results=heshiis_results,
        total=total,
    )


@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        form_name = request.form.get("form")

        if form_name == "profile":
            full_name = (request.form.get("full_name") or "").strip()
            if not full_name:
                flash(t("required_field"), "error")
            else:
                current_user.full_name = full_name
                lang = request.form.get("language")
                if lang in LANGUAGES:
                    current_user.language = lang
                db.session.commit()
                flash(t("profile_updated"), "success")
            return redirect(url_for("main.settings"))

        if form_name == "password":
            current_pwd = request.form.get("current_password") or ""
            new_pwd = request.form.get("new_password") or ""
            confirm_pwd = request.form.get("confirm_password") or ""
            if not current_user.check_password(current_pwd):
                flash(t("wrong_password"), "error")
            elif not new_pwd or new_pwd != confirm_pwd:
                flash(t("required_field"), "error")
            else:
                current_user.set_password(new_pwd)
                db.session.commit()
                flash(t("password_changed"), "success")
            return redirect(url_for("main.settings"))

    return render_template("settings.html", all_users=User.query.count())

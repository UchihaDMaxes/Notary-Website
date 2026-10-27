"""User administration (admin only)."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime

from models import db, User
from utils import t, admin_required
from translations import LANGUAGES

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.before_request
@login_required
@admin_required
def guard():
    """Every route here requires an authenticated administrator."""


@users_bp.route("/")
def list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("users/list.html", users=users)


@users_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower()
        full_name = (request.form.get("full_name") or "").strip()
        password = request.form.get("password") or ""
        role = request.form.get("role") or "staff"
        lang = request.form.get("language")
        active = bool(request.form.get("active"))

        if not username or not full_name or not password:
            flash(t("required_field"), "error")
        elif User.query.filter_by(username=username).first():
            flash(t("username_taken"), "error")
        else:
            user = User(
                username=username,
                full_name=full_name,
                role="admin" if role == "admin" else "staff",
                active=active,
                language=lang if lang in LANGUAGES else "so",
                created_at=datetime.utcnow(),
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(t("saved"), "success")
            return redirect(url_for("users.list"))

    return render_template("users/form.html", user=None)


@users_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
def edit(user_id):
    user = db.session.get(User, user_id) or abort(404)
    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower()
        full_name = (request.form.get("full_name") or "").strip()
        password = request.form.get("password") or ""
        role = request.form.get("role") or "staff"
        lang = request.form.get("language")
        active = bool(request.form.get("active"))

        existing = User.query.filter_by(username=username).first()
        if not username or not full_name:
            flash(t("required_field"), "error")
        elif existing and existing.id != user.id:
            flash(t("username_taken"), "error")
        elif user.is_admin and role != "admin" and User.query.filter_by(role="admin", active=True).count() <= 1:
            flash(t("last_admin"), "error")
        else:
            user.username = username
            user.full_name = full_name
            user.role = "admin" if role == "admin" else "staff"
            user.active = active
            if lang in LANGUAGES:
                user.language = lang
            if password:
                user.set_password(password)
            db.session.commit()
            flash(t("updated"), "success")
            return redirect(url_for("users.list"))

    return render_template("users/form.html", user=user)


@users_bp.route("/<int:user_id>/toggle", methods=["POST"])
def toggle(user_id):
    user = db.session.get(User, user_id) or abort(404)
    if user.is_admin and user.active and User.query.filter_by(role="admin", active=True).count() <= 1:
        flash(t("last_admin"), "error")
    else:
        user.active = not user.active
        db.session.commit()
        flash(t("updated"), "success")
    return redirect(url_for("users.list"))


@users_bp.route("/<int:user_id>/delete", methods=["POST"])
def delete(user_id):
    user = db.session.get(User, user_id) or abort(404)
    if user.id == current_user.id:
        flash(t("last_admin"), "error")
    elif user.is_admin and User.query.filter_by(role="admin", active=True).count() <= 1:
        flash(t("last_admin"), "error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(t("deleted"), "success")
    return redirect(url_for("users.list"))

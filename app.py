"""Application factory for the SH. ISAXAAQ Notary web app."""
import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import Config
from models import db, User
from utils import register_template_helpers, t

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    register_template_helpers(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import flash, redirect, request, url_for

        flash(t("unauthorized"), "warning")
        return redirect(url_for("auth.login", next=request.path))

    # Blueprints
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.iib import iib_bp
    from blueprints.heshiis import heshiis_bp
    from blueprints.users import users_bp
    from blueprints.scan import scan_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(iib_bp)
    app.register_blueprint(heshiis_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(scan_bp)

    # Error pages
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403, message=t("unauthorized")), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message="Server error"), 500

    # Create tables + seed the first admin on first run.
    with app.app_context():
        db.create_all()
        seed_admin()

    return app


def seed_admin():
    """Create a default administrator if no users exist yet."""
    if User.query.count() == 0:
        admin = User(
            username="admin",
            full_name="Maamulaha / Administrator",
            role="admin",
            active=True,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print(">> Seeded default admin account  (username: admin, password: admin123)")


if __name__ == "__main__":
    # Local development server. For production use `wsgi.py` with gunicorn
    # (see DEPLOY.md). Set HOST=0.0.0.0 to test from other devices on the LAN.
    application = create_app()
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "1").lower() not in ("0", "false", "no")
    application.run(host=host, port=port, debug=debug)

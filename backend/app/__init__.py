"""Flask application factory."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    if config_name == "testing":
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SECRET_KEY"] = "test-secret-key"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "DATABASE_URL", "sqlite:///bakertilly_timesheet.db"
        )
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    CORS(app, supports_credentials=True)

    from app.routes.auth import auth_bp
    from app.routes.timesheet import timesheet_bp
    from app.routes.project import project_bp
    from app.routes.client import client_bp
    from app.routes.user import user_bp
    from app.routes.report import report_bp
    from app.routes.approval import approval_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(timesheet_bp, url_prefix="/api/timesheets")
    app.register_blueprint(project_bp, url_prefix="/api/projects")
    app.register_blueprint(client_bp, url_prefix="/api/clients")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(report_bp, url_prefix="/api/reports")
    app.register_blueprint(approval_bp, url_prefix="/api/approvals")

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app):
    """Seed the default admin user if it doesn't exist."""
    from app.models.user import User

    admin = User.query.filter_by(email="admin@bakertilly.com.lr").first()
    if not admin:
        admin = User(
            email="admin@bakertilly.com.lr",
            first_name="Admin",
            last_name="User",
            role="admin",
            department="Administration",
            is_active=True,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

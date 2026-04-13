"""User model for authentication and authorization."""
from datetime import datetime, timezone
from app import db, bcrypt, login_manager
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """User model representing employees at Baker Tilly Liberia."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(
        db.String(20), nullable=False, default="staff"
    )  # admin, manager, staff
    department = db.Column(db.String(100), nullable=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=True)
    hourly_rate = db.Column(db.Float, nullable=True, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    timesheet_entries = db.relationship(
        "TimesheetEntry", backref="user", lazy="dynamic",
        foreign_keys="TimesheetEntry.user_id"
    )

    VALID_ROLES = ("admin", "manager", "staff")

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Verify a password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def is_admin(self):
        """Check if the user has admin role."""
        return self.role == "admin"

    def is_manager(self):
        """Check if the user has manager role."""
        return self.role == "manager"

    def to_dict(self):
        """Serialize user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role,
            "department": self.department,
            "employee_id": self.employee_id,
            "hourly_rate": self.hourly_rate,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@login_manager.user_loader
def load_user(user_id):
    """Load a user by ID for Flask-Login."""
    return User.query.get(int(user_id))

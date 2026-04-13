"""Client model for managing audit clients."""
from datetime import datetime, timezone
from app import db


class Client(db.Model):
    """Client model representing Baker Tilly Liberia's audit clients."""

    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    contact_person = db.Column(db.String(120), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.Text, nullable=True)
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
    projects = db.relationship("Project", backref="client", lazy="dynamic")

    def to_dict(self):
        """Serialize client to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "industry": self.industry,
            "contact_person": self.contact_person,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "address": self.address,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def validate_code(code):
        """Validate client code format (alphanumeric, 3-20 chars)."""
        if not code or not code.strip():
            return False, "Client code is required"
        code = code.strip().upper()
        if len(code) < 3 or len(code) > 20:
            return False, "Client code must be 3-20 characters"
        if not code.isalnum():
            return False, "Client code must be alphanumeric"
        return True, code

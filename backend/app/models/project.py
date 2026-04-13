"""Project model for managing audit engagements."""
from datetime import datetime, timezone
from app import db


class Project(db.Model):
    """Project model representing audit engagements."""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(
        db.String(20), nullable=False, default="active"
    )  # active, completed, on_hold, cancelled
    budget_hours = db.Column(db.Float, nullable=True, default=0.0)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    engagement_type = db.Column(
        db.String(50), nullable=True
    )  # audit, tax, advisory, other
    is_billable = db.Column(db.Boolean, default=True)
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
        "TimesheetEntry", backref="project", lazy="dynamic"
    )
    manager = db.relationship("User", foreign_keys=[manager_id])

    VALID_STATUSES = ("active", "completed", "on_hold", "cancelled")
    VALID_ENGAGEMENT_TYPES = ("audit", "tax", "advisory", "other")

    @property
    def total_hours_logged(self):
        """Calculate total hours logged against this project."""
        from app.models.timesheet import TimesheetEntry

        result = (
            db.session.query(db.func.sum(TimesheetEntry.hours))
            .filter(TimesheetEntry.project_id == self.id)
            .scalar()
        )
        return result or 0.0

    @property
    def budget_utilization(self):
        """Calculate percentage of budget hours used."""
        if not self.budget_hours or self.budget_hours <= 0:
            return 0.0
        return round((self.total_hours_logged / self.budget_hours) * 100, 2)

    def to_dict(self):
        """Serialize project to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "client_id": self.client_id,
            "client_name": self.client.name if self.client else None,
            "manager_id": self.manager_id,
            "manager_name": self.manager.full_name if self.manager else None,
            "status": self.status,
            "budget_hours": self.budget_hours,
            "total_hours_logged": self.total_hours_logged,
            "budget_utilization": self.budget_utilization,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "engagement_type": self.engagement_type,
            "is_billable": self.is_billable,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

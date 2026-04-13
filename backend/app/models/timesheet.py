"""Timesheet entry model for tracking work hours."""
from datetime import datetime, date, timezone
from app import db


class TimesheetEntry(db.Model):
    """Model representing a single timesheet entry."""

    __tablename__ = "timesheet_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_billable = db.Column(db.Boolean, default=True)
    status = db.Column(
        db.String(20), nullable=False, default="draft"
    )  # draft, submitted, approved, rejected
    rejection_reason = db.Column(db.Text, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    approver = db.relationship("User", foreign_keys=[approved_by])

    VALID_STATUSES = ("draft", "submitted", "approved", "rejected")
    MAX_DAILY_HOURS = 24.0
    MIN_ENTRY_HOURS = 0.25

    @staticmethod
    def validate_hours(hours):
        """Validate that hours are within acceptable range."""
        if hours is None:
            return False, "Hours are required"
        try:
            hours = float(hours)
        except (ValueError, TypeError):
            return False, "Hours must be a number"
        if hours < TimesheetEntry.MIN_ENTRY_HOURS:
            return False, f"Minimum entry is {TimesheetEntry.MIN_ENTRY_HOURS} hours"
        if hours > TimesheetEntry.MAX_DAILY_HOURS:
            return False, f"Maximum daily hours is {TimesheetEntry.MAX_DAILY_HOURS}"
        return True, hours

    @staticmethod
    def validate_date(entry_date):
        """Validate the entry date."""
        if entry_date is None:
            return False, "Date is required"
        if isinstance(entry_date, str):
            try:
                entry_date = date.fromisoformat(entry_date)
            except ValueError:
                return False, "Invalid date format. Use YYYY-MM-DD"
        today = date.today()
        if entry_date > today:
            return False, "Cannot log time for future dates"
        return True, entry_date

    def submit(self):
        """Submit the timesheet entry for approval."""
        if self.status != "draft" and self.status != "rejected":
            return False, "Only draft or rejected entries can be submitted"
        self.status = "submitted"
        self.submitted_at = datetime.now(timezone.utc)
        self.rejection_reason = None
        return True, "Entry submitted successfully"

    def approve(self, approver_id):
        """Approve the timesheet entry."""
        if self.status != "submitted":
            return False, "Only submitted entries can be approved"
        if self.user_id == approver_id:
            return False, "Cannot approve your own timesheet entry"
        self.status = "approved"
        self.approved_by = approver_id
        self.approved_at = datetime.now(timezone.utc)
        return True, "Entry approved successfully"

    def reject(self, approver_id, reason):
        """Reject the timesheet entry."""
        if self.status != "submitted":
            return False, "Only submitted entries can be rejected"
        if not reason or not reason.strip():
            return False, "Rejection reason is required"
        self.status = "rejected"
        self.approved_by = approver_id
        self.approved_at = datetime.now(timezone.utc)
        self.rejection_reason = reason.strip()
        return True, "Entry rejected"

    def to_dict(self):
        """Serialize timesheet entry to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else None,
            "project_id": self.project_id,
            "project_name": self.project.name if self.project else None,
            "project_code": self.project.code if self.project else None,
            "date": self.date.isoformat() if self.date else None,
            "hours": self.hours,
            "description": self.description,
            "is_billable": self.is_billable,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "approved_by": self.approved_by,
            "approver_name": self.approver.full_name if self.approver else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "submitted_at": (
                self.submitted_at.isoformat() if self.submitted_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

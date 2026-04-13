"""Timesheet business logic service."""
from datetime import date, datetime, timezone
from app import db
from app.models.timesheet import TimesheetEntry
from app.models.project import Project


class TimesheetService:
    """Service class for timesheet operations."""

    @staticmethod
    def create_entry(user_id, project_id, entry_date, hours, description=None, is_billable=True):
        """Create a new timesheet entry."""
        # Validate project exists and is active
        project = Project.query.get(project_id)
        if not project:
            return None, "Project not found"
        if project.status != "active":
            return None, "Project is not active"

        # Validate hours
        valid, result = TimesheetEntry.validate_hours(hours)
        if not valid:
            return None, result
        hours = result

        # Validate date
        valid, result = TimesheetEntry.validate_date(entry_date)
        if not valid:
            return None, result
        entry_date = result

        # Check total hours for the day
        existing_hours = TimesheetService.get_daily_total(user_id, entry_date)
        if existing_hours + hours > TimesheetEntry.MAX_DAILY_HOURS:
            return None, f"Total daily hours would exceed {TimesheetEntry.MAX_DAILY_HOURS}"

        entry = TimesheetEntry(
            user_id=user_id,
            project_id=project_id,
            date=entry_date,
            hours=hours,
            description=description,
            is_billable=is_billable,
            status="draft",
        )
        db.session.add(entry)
        db.session.commit()
        return entry, "Entry created successfully"

    @staticmethod
    def update_entry(entry_id, user_id, **kwargs):
        """Update an existing timesheet entry."""
        entry = TimesheetEntry.query.get(entry_id)
        if not entry:
            return None, "Entry not found"
        if entry.user_id != user_id:
            return None, "Not authorized to update this entry"
        if entry.status not in ("draft", "rejected"):
            return None, "Only draft or rejected entries can be edited"

        if "hours" in kwargs:
            valid, result = TimesheetEntry.validate_hours(kwargs["hours"])
            if not valid:
                return None, result
            entry.hours = result

        if "date" in kwargs:
            valid, result = TimesheetEntry.validate_date(kwargs["date"])
            if not valid:
                return None, result
            entry.date = result

        if "project_id" in kwargs:
            project = Project.query.get(kwargs["project_id"])
            if not project:
                return None, "Project not found"
            entry.project_id = kwargs["project_id"]

        if "description" in kwargs:
            entry.description = kwargs["description"]

        if "is_billable" in kwargs:
            entry.is_billable = kwargs["is_billable"]

        db.session.commit()
        return entry, "Entry updated successfully"

    @staticmethod
    def delete_entry(entry_id, user_id):
        """Delete a timesheet entry."""
        entry = TimesheetEntry.query.get(entry_id)
        if not entry:
            return False, "Entry not found"
        if entry.user_id != user_id:
            return False, "Not authorized to delete this entry"
        if entry.status not in ("draft", "rejected"):
            return False, "Only draft or rejected entries can be deleted"

        db.session.delete(entry)
        db.session.commit()
        return True, "Entry deleted successfully"

    @staticmethod
    def get_daily_total(user_id, target_date):
        """Get total hours logged for a specific day."""
        result = (
            db.session.query(db.func.sum(TimesheetEntry.hours))
            .filter(
                TimesheetEntry.user_id == user_id,
                TimesheetEntry.date == target_date,
            )
            .scalar()
        )
        return result or 0.0

    @staticmethod
    def get_weekly_entries(user_id, start_date, end_date):
        """Get all entries for a user within a date range."""
        return (
            TimesheetEntry.query.filter(
                TimesheetEntry.user_id == user_id,
                TimesheetEntry.date >= start_date,
                TimesheetEntry.date <= end_date,
            )
            .order_by(TimesheetEntry.date.asc())
            .all()
        )

    @staticmethod
    def submit_entries(user_id, entry_ids):
        """Submit multiple timesheet entries for approval."""
        entries = TimesheetEntry.query.filter(
            TimesheetEntry.id.in_(entry_ids),
            TimesheetEntry.user_id == user_id,
        ).all()

        if not entries:
            return [], "No entries found"

        submitted = []
        errors = []
        for entry in entries:
            success, msg = entry.submit()
            if success:
                submitted.append(entry)
            else:
                errors.append(f"Entry {entry.id}: {msg}")

        db.session.commit()
        return submitted, errors if errors else "All entries submitted"

    @staticmethod
    def get_pending_approvals(manager_id=None):
        """Get all entries pending approval, optionally filtered by manager's projects."""
        query = TimesheetEntry.query.filter(TimesheetEntry.status == "submitted")
        if manager_id:
            query = query.join(Project).filter(Project.manager_id == manager_id)
        return query.order_by(TimesheetEntry.submitted_at.asc()).all()

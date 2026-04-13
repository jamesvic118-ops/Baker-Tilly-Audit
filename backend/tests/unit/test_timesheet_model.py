"""Tests for the Timesheet model."""
import pytest
from datetime import date, datetime, timezone
from app.models.timesheet import TimesheetEntry


class TestTimesheetEntry:
    """Test suite for TimesheetEntry model."""

    def test_validate_hours_valid(self):
        """Test valid hours validation."""
        valid, result = TimesheetEntry.validate_hours(8.0)
        assert valid is True
        assert result == 8.0

    def test_validate_hours_minimum(self):
        """Test minimum hours validation."""
        valid, result = TimesheetEntry.validate_hours(0.1)
        assert valid is False
        assert "Minimum" in result

    def test_validate_hours_maximum(self):
        """Test maximum hours validation."""
        valid, result = TimesheetEntry.validate_hours(25)
        assert valid is False
        assert "Maximum" in result

    def test_validate_hours_none(self):
        """Test None hours validation."""
        valid, result = TimesheetEntry.validate_hours(None)
        assert valid is False

    def test_validate_hours_string(self):
        """Test string hours conversion."""
        valid, result = TimesheetEntry.validate_hours("4.5")
        assert valid is True
        assert result == 4.5

    def test_validate_hours_invalid_string(self):
        """Test invalid string hours."""
        valid, result = TimesheetEntry.validate_hours("abc")
        assert valid is False

    def test_validate_date_valid(self):
        """Test valid date validation."""
        today = date.today()
        valid, result = TimesheetEntry.validate_date(today)
        assert valid is True
        assert result == today

    def test_validate_date_string(self):
        """Test string date validation."""
        valid, result = TimesheetEntry.validate_date("2024-01-15")
        assert valid is True
        assert result == date(2024, 1, 15)

    def test_validate_date_none(self):
        """Test None date validation."""
        valid, result = TimesheetEntry.validate_date(None)
        assert valid is False

    def test_validate_date_invalid_string(self):
        """Test invalid date string."""
        valid, result = TimesheetEntry.validate_date("not-a-date")
        assert valid is False

    def test_submit_draft_entry(self, db, staff_user, sample_project):
        """Test submitting a draft entry."""
        entry = TimesheetEntry(
            user_id=staff_user.id,
            project_id=sample_project.id,
            date=date.today(),
            hours=8.0,
            status="draft",
        )
        db.session.add(entry)
        db.session.commit()

        success, msg = entry.submit()
        assert success is True
        assert entry.status == "submitted"
        assert entry.submitted_at is not None

    def test_submit_approved_entry_fails(self, db, staff_user, sample_project):
        """Test that submitting an approved entry fails."""
        entry = TimesheetEntry(
            user_id=staff_user.id,
            project_id=sample_project.id,
            date=date.today(),
            hours=4.0,
            status="approved",
        )
        db.session.add(entry)
        db.session.commit()

        success, msg = entry.submit()
        assert success is False

    def test_approve_submitted_entry(self, db, staff_user, manager_user, sample_project):
        """Test approving a submitted entry."""
        entry = TimesheetEntry(
            user_id=staff_user.id,
            project_id=sample_project.id,
            date=date.today(),
            hours=8.0,
            status="submitted",
        )
        db.session.add(entry)
        db.session.commit()

        success, msg = entry.approve(manager_user.id)
        assert success is True
        assert entry.status == "approved"
        assert entry.approved_by == manager_user.id

    def test_approve_own_entry_fails(self, db, staff_user, sample_project):
        """Test that a user cannot approve their own entry."""
        entry = TimesheetEntry(
            user_id=staff_user.id,
            project_id=sample_project.id,
            date=date.today(),
            hours=8.0,
            status="submitted",
        )
        db.session.add(entry)
        db.session.commit()

        success, msg = entry.approve(staff_user.id)
        assert success is False
        assert "own" in msg.lower()

    def test_reject_submitted_entry(self, db, staff_user, manager_user, sample_project):
        """Test rejecting a submitted entry."""
        entry = TimesheetEntry(
            user_id=staff_user.id,
            project_id=sample_project.id,
            date=date.today(),
            hours=8.0,
            status="submitted",
        )
        db.session.add(entry)
        db.session.commit()

        success, msg = entry.reject(manager_user.id, "Hours seem too high")
        assert success is True
        assert entry.status == "rejected"
        assert entry.rejection_reason == "Hours seem too high"

    def test_reject_without_reason_fails(self, db, staff_user, manager_user, sample_project):
        """Test that rejection without reason fails."""
        entry = TimesheetEntry(
            user_id=staff_user.id,
            project_id=sample_project.id,
            date=date.today(),
            hours=8.0,
            status="submitted",
        )
        db.session.add(entry)
        db.session.commit()

        success, msg = entry.reject(manager_user.id, "")
        assert success is False

    def test_to_dict(self, db, staff_user, sample_project):
        """Test serialization to dictionary."""
        entry = TimesheetEntry(
            user_id=staff_user.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            hours=6.5,
            description="Audit fieldwork",
            is_billable=True,
            status="draft",
        )
        db.session.add(entry)
        db.session.commit()

        d = entry.to_dict()
        assert d["hours"] == 6.5
        assert d["description"] == "Audit fieldwork"
        assert d["is_billable"] is True
        assert d["status"] == "draft"
        assert d["date"] == "2024-01-15"

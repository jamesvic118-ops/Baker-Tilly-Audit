"""Tests for the timesheet service."""
import json
from datetime import date, timedelta
from app.models.timesheet import TimesheetEntry
from app.models.project import Project
from app.services.timesheet_service import TimesheetService


class TestTimesheetServiceCreate:
    """Tests for TimesheetService.create_entry."""

    def test_create_entry_success(self, app, db, staff_user, sample_project):
        """Test creating a valid timesheet entry."""
        with app.app_context():
            entry, msg = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
                description="Audit work",
                is_billable=True,
            )
            assert entry is not None
            assert entry.hours == 8.0
            assert entry.status == "draft"

    def test_create_entry_invalid_project(self, app, db, staff_user):
        """Test creating entry with non-existent project."""
        with app.app_context():
            entry, msg = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=9999,
                entry_date=date.today(),
                hours=8.0,
            )
            assert entry is None
            assert "not found" in msg.lower()

    def test_create_entry_inactive_project(self, app, db, staff_user, sample_project):
        """Test creating entry with inactive project."""
        with app.app_context():
            sample_project.status = "completed"
            db.session.commit()
            entry, msg = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            assert entry is None
            assert "not active" in msg.lower()

    def test_create_entry_invalid_hours(self, app, db, staff_user, sample_project):
        """Test creating entry with invalid hours."""
        with app.app_context():
            entry, msg = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=0.1,
            )
            assert entry is None

    def test_create_entry_exceeds_daily_max(self, app, db, staff_user, sample_project):
        """Test creating entry that would exceed daily max."""
        with app.app_context():
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=20.0,
            )
            entry, msg = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
            assert entry is None
            assert "exceed" in msg.lower()

    def test_create_entry_non_billable(self, app, db, staff_user, sample_project):
        """Test creating a non-billable entry."""
        with app.app_context():
            entry, msg = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=2.0,
                is_billable=False,
            )
            assert entry is not None
            assert entry.is_billable is False


class TestTimesheetServiceUpdate:
    """Tests for TimesheetService.update_entry."""

    def test_update_entry_success(self, app, db, staff_user, sample_project):
        """Test updating a draft entry."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            updated, msg = TimesheetService.update_entry(
                entry.id, staff_user.id, hours=6.0, description="Updated"
            )
            assert updated is not None
            assert updated.hours == 6.0
            assert updated.description == "Updated"

    def test_update_entry_not_found(self, app, db, staff_user):
        """Test updating a non-existent entry."""
        with app.app_context():
            result, msg = TimesheetService.update_entry(9999, staff_user.id, hours=5)
            assert result is None
            assert "not found" in msg.lower()

    def test_update_entry_wrong_user(self, app, db, staff_user, manager_user, sample_project):
        """Test that a user cannot update another user's entry."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            result, msg = TimesheetService.update_entry(entry.id, manager_user.id, hours=6)
            assert result is None
            assert "not authorized" in msg.lower()

    def test_update_submitted_entry_fails(self, app, db, staff_user, sample_project):
        """Test that a submitted entry cannot be updated."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            entry.submit()
            db.session.commit()
            result, msg = TimesheetService.update_entry(entry.id, staff_user.id, hours=6)
            assert result is None

    def test_update_entry_change_project(self, app, db, staff_user, sample_project, sample_client):
        """Test updating the project of an entry."""
        with app.app_context():
            p2 = Project(name="P2", code="P2CODE", client_id=sample_client.id, status="active")
            db.session.add(p2)
            db.session.commit()
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            result, msg = TimesheetService.update_entry(entry.id, staff_user.id, project_id=p2.id)
            assert result is not None
            assert result.project_id == p2.id


class TestTimesheetServiceDelete:
    """Tests for TimesheetService.delete_entry."""

    def test_delete_entry_success(self, app, db, staff_user, sample_project):
        """Test deleting a draft entry."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            success, msg = TimesheetService.delete_entry(entry.id, staff_user.id)
            assert success is True

    def test_delete_entry_not_found(self, app, db, staff_user):
        """Test deleting a non-existent entry."""
        with app.app_context():
            success, msg = TimesheetService.delete_entry(9999, staff_user.id)
            assert success is False

    def test_delete_entry_wrong_user(self, app, db, staff_user, manager_user, sample_project):
        """Test that a user cannot delete another user's entry."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            success, msg = TimesheetService.delete_entry(entry.id, manager_user.id)
            assert success is False

    def test_delete_approved_entry_fails(self, app, db, staff_user, manager_user, sample_project):
        """Test that an approved entry cannot be deleted."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            entry.submit()
            entry.approve(manager_user.id)
            db.session.commit()
            success, msg = TimesheetService.delete_entry(entry.id, staff_user.id)
            assert success is False


class TestTimesheetServiceQueries:
    """Tests for TimesheetService query methods."""

    def test_get_daily_total(self, app, db, staff_user, sample_project):
        """Test getting daily total hours."""
        with app.app_context():
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=3.0,
            )
            total = TimesheetService.get_daily_total(staff_user.id, date.today())
            assert total == 7.0

    def test_get_daily_total_empty(self, app, db, staff_user):
        """Test daily total with no entries."""
        with app.app_context():
            total = TimesheetService.get_daily_total(staff_user.id, date.today())
            assert total == 0.0

    def test_get_weekly_entries(self, app, db, staff_user, sample_project):
        """Test getting weekly entries."""
        with app.app_context():
            today = date.today()
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=today,
                hours=8.0,
            )
            entries = TimesheetService.get_weekly_entries(
                staff_user.id, today - timedelta(days=7), today
            )
            assert len(entries) >= 1

    def test_submit_entries(self, app, db, staff_user, sample_project):
        """Test submitting multiple entries."""
        with app.app_context():
            e1, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            e2, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=3.0,
            )
            submitted, result = TimesheetService.submit_entries(
                staff_user.id, [e1.id, e2.id]
            )
            assert len(submitted) == 2

    def test_submit_no_entries(self, app, db, staff_user):
        """Test submitting with no matching entries."""
        with app.app_context():
            submitted, result = TimesheetService.submit_entries(staff_user.id, [999])
            assert len(submitted) == 0

    def test_get_pending_approvals(self, app, db, staff_user, manager_user, sample_project):
        """Test getting pending approvals."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
            entry.submit()
            db.session.commit()
            pending = TimesheetService.get_pending_approvals()
            assert len(pending) >= 1

    def test_get_pending_approvals_by_manager(self, app, db, staff_user, manager_user, sample_project):
        """Test getting pending approvals filtered by manager."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
            entry.submit()
            db.session.commit()
            pending = TimesheetService.get_pending_approvals(manager_id=manager_user.id)
            assert len(pending) >= 1

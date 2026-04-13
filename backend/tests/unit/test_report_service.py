"""Tests for the report service."""
from datetime import date, timedelta
from app.services.report_service import ReportService
from app.services.timesheet_service import TimesheetService


class TestUserSummary:
    """Tests for ReportService.get_user_summary."""

    def test_user_summary_with_entries(self, app, db, staff_user, sample_project):
        """Test user summary with timesheet entries."""
        with app.app_context():
            today = date.today()
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=today,
                hours=6.0,
                is_billable=True,
            )
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=today,
                hours=2.0,
                is_billable=False,
            )
            summary = ReportService.get_user_summary(
                staff_user.id, today - timedelta(days=7), today
            )
            assert summary["total_hours"] == 8.0
            assert summary["billable_hours"] == 6.0
            assert summary["non_billable_hours"] == 2.0
            assert summary["utilization_rate"] == 75.0
            assert summary["entry_count"] == 2

    def test_user_summary_empty(self, app, db, staff_user):
        """Test user summary with no entries."""
        with app.app_context():
            today = date.today()
            summary = ReportService.get_user_summary(
                staff_user.id, today - timedelta(days=7), today
            )
            assert summary["total_hours"] == 0
            assert summary["utilization_rate"] == 0
            assert summary["entry_count"] == 0

    def test_user_summary_by_project(self, app, db, staff_user, sample_project):
        """Test that summary breaks down by project."""
        with app.app_context():
            today = date.today()
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=today,
                hours=4.0,
            )
            summary = ReportService.get_user_summary(
                staff_user.id, today - timedelta(days=7), today
            )
            assert sample_project.name in summary["by_project"]

    def test_user_summary_by_status(self, app, db, staff_user, sample_project):
        """Test that summary breaks down by status."""
        with app.app_context():
            today = date.today()
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=today,
                hours=4.0,
            )
            summary = ReportService.get_user_summary(
                staff_user.id, today - timedelta(days=7), today
            )
            assert "draft" in summary["by_status"]


class TestProjectSummary:
    """Tests for ReportService.get_project_summary."""

    def test_project_summary(self, app, db, staff_user, sample_project):
        """Test project summary with entries."""
        with app.app_context():
            today = date.today()
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=today,
                hours=8.0,
                is_billable=True,
            )
            summary = ReportService.get_project_summary(sample_project.id)
            assert summary["total_hours"] == 8.0
            assert summary["billable_hours"] == 8.0
            assert summary["project_name"] == sample_project.name

    def test_project_summary_with_date_range(self, app, db, staff_user, sample_project):
        """Test project summary with date filtering."""
        with app.app_context():
            today = date.today()
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=today,
                hours=8.0,
            )
            summary = ReportService.get_project_summary(
                sample_project.id, today - timedelta(days=1), today
            )
            assert summary["entry_count"] == 1

    def test_project_summary_by_user(self, app, db, staff_user, sample_project):
        """Test that project summary breaks down by user."""
        with app.app_context():
            today = date.today()
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=today,
                hours=4.0,
            )
            summary = ReportService.get_project_summary(sample_project.id)
            assert staff_user.full_name in summary["by_user"]


class TestTeamSummary:
    """Tests for ReportService.get_team_summary."""

    def test_team_summary(self, app, db, staff_user, manager_user, sample_project):
        """Test team summary with entries from multiple users."""
        with app.app_context():
            today = date.today()
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=today,
                hours=8.0,
                is_billable=True,
            )
            summary = ReportService.get_team_summary(
                today - timedelta(days=7), today
            )
            assert len(summary["team"]) >= 1
            assert summary["team"][0]["total_hours"] == 8.0

    def test_team_summary_empty(self, app, db):
        """Test team summary with no entries."""
        with app.app_context():
            today = date.today()
            summary = ReportService.get_team_summary(
                today - timedelta(days=7), today
            )
            assert len(summary["team"]) == 0

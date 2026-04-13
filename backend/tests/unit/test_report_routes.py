"""Tests for report routes."""
import json
from datetime import date, timedelta
from app.services.timesheet_service import TimesheetService


class TestReportRoutes:
    """Test suite for report API endpoints."""

    def test_my_summary_default(self, client, db, staff_user, staff_token):
        """Test getting current user's summary with default dates."""
        response = client.get(
            "/api/reports/my-summary",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "summary" in data

    def test_my_summary_with_dates(self, client, db, staff_user, staff_token):
        """Test getting summary with specific date range."""
        today = date.today()
        start = (today - timedelta(days=30)).isoformat()
        end = today.isoformat()
        response = client.get(
            f"/api/reports/my-summary?start_date={start}&end_date={end}",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_my_summary_with_entries(self, client, app, db, staff_user, staff_token, sample_project):
        """Test summary includes actual timesheet data."""
        with app.app_context():
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=6.0,
                is_billable=True,
            )
        today = date.today()
        response = client.get(
            f"/api/reports/my-summary?start_date={today.isoformat()}&end_date={today.isoformat()}",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()["summary"]
        assert data["total_hours"] == 6.0

    def test_user_summary_as_admin(self, client, db, admin_user, admin_token, staff_user):
        """Test getting another user's summary as admin."""
        response = client.get(
            f"/api/reports/user/{staff_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

    def test_user_summary_staff_forbidden(self, client, db, staff_user, staff_token):
        """Test that staff cannot access other user summaries."""
        response = client.get(
            "/api/reports/user/1",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 403

    def test_project_summary(self, client, db, staff_user, staff_token, sample_project):
        """Test getting project summary."""
        response = client.get(
            f"/api/reports/project/{sample_project.id}",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_project_summary_with_dates(self, client, db, staff_user, staff_token, sample_project):
        """Test project summary with date range."""
        today = date.today()
        response = client.get(
            f"/api/reports/project/{sample_project.id}?start_date={today.isoformat()}&end_date={today.isoformat()}",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_team_summary_as_admin(self, client, db, admin_user, admin_token):
        """Test getting team summary as admin."""
        response = client.get(
            "/api/reports/team",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

    def test_team_summary_with_dates(self, client, db, admin_user, admin_token):
        """Test team summary with specific dates."""
        today = date.today()
        start = (today - timedelta(days=30)).isoformat()
        response = client.get(
            f"/api/reports/team?start_date={start}&end_date={today.isoformat()}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

    def test_team_summary_staff_forbidden(self, client, db, staff_user, staff_token):
        """Test that staff cannot access team summary."""
        response = client.get(
            "/api/reports/team",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 403

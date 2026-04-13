"""Tests for timesheet routes."""
import json
from datetime import date
from app.models.timesheet import TimesheetEntry
from app.services.timesheet_service import TimesheetService


class TestTimesheetRoutes:
    """Test suite for timesheet API endpoints."""

    def test_list_entries_empty(self, client, db, staff_user, staff_token):
        """Test listing entries when none exist."""
        response = client.get(
            "/api/timesheets",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["entries"] == []

    def test_list_entries_with_data(self, client, app, db, staff_user, staff_token, sample_project):
        """Test listing entries with data."""
        with app.app_context():
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
        response = client.get(
            "/api/timesheets",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200
        assert len(response.get_json()["entries"]) == 1

    def test_list_entries_with_filters(self, client, app, db, staff_user, staff_token, sample_project):
        """Test listing entries with date and status filters."""
        with app.app_context():
            TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
        today = date.today().isoformat()
        response = client.get(
            f"/api/timesheets?start_date={today}&end_date={today}&status=draft",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_create_entry(self, client, db, staff_user, staff_token, sample_project):
        """Test creating a timesheet entry via API."""
        response = client.post(
            "/api/timesheets",
            data=json.dumps({
                "project_id": sample_project.id,
                "date": date.today().isoformat(),
                "hours": 6.0,
                "description": "Fieldwork",
                "is_billable": True,
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["entry"]["hours"] == 6.0

    def test_create_entry_no_body(self, client, db, staff_user, staff_token):
        """Test creating entry without request body."""
        response = client.post(
            "/api/timesheets",
            content_type="application/json",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 400

    def test_get_entry(self, client, app, db, staff_user, staff_token, sample_project):
        """Test getting a specific entry."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            entry_id = entry.id
        response = client.get(
            f"/api/timesheets/{entry_id}",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_get_entry_not_found(self, client, db, staff_user, staff_token):
        """Test getting a non-existent entry."""
        response = client.get(
            "/api/timesheets/9999",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 404

    def test_get_entry_forbidden(self, client, app, db, staff_user, manager_user, manager_token, sample_project):
        """Test getting another user's entry as non-admin."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            entry_id = entry.id
        response = client.get(
            f"/api/timesheets/{entry_id}",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 403

    def test_update_entry(self, client, app, db, staff_user, staff_token, sample_project):
        """Test updating a timesheet entry."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            entry_id = entry.id
        response = client.put(
            f"/api/timesheets/{entry_id}",
            data=json.dumps({"hours": 6.0, "description": "Updated"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_delete_entry(self, client, app, db, staff_user, staff_token, sample_project):
        """Test deleting a timesheet entry."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            entry_id = entry.id
        response = client.delete(
            f"/api/timesheets/{entry_id}",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_submit_entries(self, client, app, db, staff_user, staff_token, sample_project):
        """Test submitting entries for approval."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
            entry_id = entry.id
        response = client.post(
            "/api/timesheets/submit",
            data=json.dumps({"entry_ids": [entry_id]}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_submit_entries_no_body(self, client, db, staff_user, staff_token):
        """Test submitting with no request body."""
        response = client.post(
            "/api/timesheets/submit",
            content_type="application/json",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 400

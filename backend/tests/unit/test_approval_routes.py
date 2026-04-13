"""Tests for approval routes."""
import json
from datetime import date
from app.services.timesheet_service import TimesheetService


class TestApprovalRoutes:
    """Test suite for approval API endpoints."""

    def test_list_pending_as_admin(self, client, app, db, admin_user, admin_token, staff_user, sample_project):
        """Test listing pending entries as admin."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
            entry.submit()
            db.session.commit()
        response = client.get(
            "/api/approvals/pending",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert len(response.get_json()["entries"]) >= 1

    def test_list_pending_as_manager(self, client, app, db, manager_user, manager_token, staff_user, sample_project):
        """Test listing pending entries as manager."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
            entry.submit()
            db.session.commit()
        response = client.get(
            "/api/approvals/pending",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 200

    def test_list_pending_staff_forbidden(self, client, db, staff_user, staff_token):
        """Test that staff cannot access pending approvals."""
        response = client.get(
            "/api/approvals/pending",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 403

    def test_approve_entry(self, client, app, db, admin_user, admin_token, staff_user, sample_project):
        """Test approving a timesheet entry."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
            entry.submit()
            db.session.commit()
            entry_id = entry.id
        response = client.post(
            f"/api/approvals/approve/{entry_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["entry"]["status"] == "approved"

    def test_approve_entry_not_found(self, client, db, admin_user, admin_token):
        """Test approving non-existent entry."""
        response = client.post(
            "/api/approvals/approve/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_approve_draft_entry_fails(self, client, app, db, admin_user, admin_token, staff_user, sample_project):
        """Test approving a draft entry (should fail)."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            entry_id = entry.id
        response = client.post(
            f"/api/approvals/approve/{entry_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_reject_entry(self, client, app, db, admin_user, admin_token, staff_user, sample_project):
        """Test rejecting a timesheet entry."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
            entry.submit()
            db.session.commit()
            entry_id = entry.id
        response = client.post(
            f"/api/approvals/reject/{entry_id}",
            data=json.dumps({"reason": "Hours seem too high"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["entry"]["status"] == "rejected"

    def test_reject_entry_not_found(self, client, db, admin_user, admin_token):
        """Test rejecting non-existent entry."""
        response = client.post(
            "/api/approvals/reject/9999",
            data=json.dumps({"reason": "test"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_reject_entry_no_reason(self, client, app, db, admin_user, admin_token, staff_user, sample_project):
        """Test rejecting without a reason."""
        with app.app_context():
            entry, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=8.0,
            )
            entry.submit()
            db.session.commit()
            entry_id = entry.id
        response = client.post(
            f"/api/approvals/reject/{entry_id}",
            data=json.dumps({"reason": ""}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_batch_approve(self, client, app, db, admin_user, admin_token, staff_user, sample_project):
        """Test batch approving entries."""
        with app.app_context():
            e1, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=4.0,
            )
            e1.submit()
            e2, _ = TimesheetService.create_entry(
                user_id=staff_user.id,
                project_id=sample_project.id,
                entry_date=date.today(),
                hours=3.0,
            )
            e2.submit()
            db.session.commit()
            ids = [e1.id, e2.id]
        response = client.post(
            "/api/approvals/batch-approve",
            data=json.dumps({"entry_ids": ids}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["approved"]) == 2

    def test_batch_approve_no_body(self, client, db, admin_user, admin_token):
        """Test batch approve without body."""
        response = client.post(
            "/api/approvals/batch-approve",
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_batch_approve_nonexistent_entries(self, client, db, admin_user, admin_token):
        """Test batch approve with non-existent entries."""
        response = client.post(
            "/api/approvals/batch-approve",
            data=json.dumps({"entry_ids": [9999]}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["errors"]) >= 1

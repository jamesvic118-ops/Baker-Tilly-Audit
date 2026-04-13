"""Tests for project routes."""
import json
from app.models.project import Project


class TestProjectRoutes:
    """Test suite for project API endpoints."""

    def test_list_projects(self, client, db, staff_user, staff_token, sample_project):
        """Test listing projects."""
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200
        assert len(response.get_json()["projects"]) >= 1

    def test_list_projects_filter_status(self, client, db, staff_user, staff_token, sample_project):
        """Test listing projects with status filter."""
        response = client.get(
            "/api/projects?status=all",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_list_projects_filter_client(self, client, db, staff_user, staff_token, sample_project, sample_client):
        """Test listing projects filtered by client."""
        response = client.get(
            f"/api/projects?client_id={sample_client.id}",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_get_project(self, client, db, staff_user, staff_token, sample_project):
        """Test getting a specific project."""
        response = client.get(
            f"/api/projects/{sample_project.id}",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["project"]["name"] == sample_project.name

    def test_get_project_not_found(self, client, db, staff_user, staff_token):
        """Test getting a non-existent project."""
        response = client.get(
            "/api/projects/9999",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 404

    def test_create_project(self, client, db, admin_user, admin_token, sample_client):
        """Test creating a new project."""
        response = client.post(
            "/api/projects",
            data=json.dumps({
                "name": "New Audit",
                "code": "NAUD01",
                "client_id": sample_client.id,
                "budget_hours": 200,
                "engagement_type": "audit",
                "is_billable": True,
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201

    def test_create_project_missing_name(self, client, db, admin_user, admin_token, sample_client):
        """Test creating a project without a name."""
        response = client.post(
            "/api/projects",
            data=json.dumps({"code": "X", "client_id": sample_client.id}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_create_project_missing_code(self, client, db, admin_user, admin_token, sample_client):
        """Test creating a project without a code."""
        response = client.post(
            "/api/projects",
            data=json.dumps({"name": "Test", "client_id": sample_client.id}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_create_project_missing_client(self, client, db, admin_user, admin_token):
        """Test creating a project without a client."""
        response = client.post(
            "/api/projects",
            data=json.dumps({"name": "Test", "code": "TST01"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_create_project_duplicate_code(self, client, db, admin_user, admin_token, sample_project, sample_client):
        """Test creating a project with duplicate code."""
        response = client.post(
            "/api/projects",
            data=json.dumps({
                "name": "Dup",
                "code": sample_project.code,
                "client_id": sample_client.id,
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 409

    def test_create_project_invalid_client(self, client, db, admin_user, admin_token):
        """Test creating project with non-existent client."""
        response = client.post(
            "/api/projects",
            data=json.dumps({"name": "Test", "code": "TST02", "client_id": 9999}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_create_project_staff_forbidden(self, client, db, staff_user, staff_token, sample_client):
        """Test that staff cannot create projects."""
        response = client.post(
            "/api/projects",
            data=json.dumps({"name": "Test", "code": "TST03", "client_id": sample_client.id}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 403

    def test_update_project(self, client, db, admin_user, admin_token, sample_project):
        """Test updating a project."""
        response = client.put(
            f"/api/projects/{sample_project.id}",
            data=json.dumps({"name": "Updated Name", "status": "completed", "budget_hours": 150}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["project"]["name"] == "Updated Name"
        assert data["project"]["status"] == "completed"

    def test_update_project_not_found(self, client, db, admin_user, admin_token):
        """Test updating a non-existent project."""
        response = client.put(
            "/api/projects/9999",
            data=json.dumps({"name": "X"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_update_project_invalid_status(self, client, db, admin_user, admin_token, sample_project):
        """Test updating project with invalid status."""
        response = client.put(
            f"/api/projects/{sample_project.id}",
            data=json.dumps({"status": "invalid"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_create_project_with_dates(self, client, db, admin_user, admin_token, sample_client):
        """Test creating project with start and end dates."""
        response = client.post(
            "/api/projects",
            data=json.dumps({
                "name": "Dated Project",
                "code": "DATED1",
                "client_id": sample_client.id,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201

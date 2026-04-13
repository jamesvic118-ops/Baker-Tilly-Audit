"""Tests for client routes."""
import json


class TestClientRoutes:
    """Test suite for client API endpoints."""

    def test_list_clients(self, client, db, staff_user, staff_token, sample_client):
        """Test listing active clients."""
        response = client.get(
            "/api/clients",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200
        assert len(response.get_json()["clients"]) >= 1

    def test_list_clients_include_inactive(self, client, db, staff_user, staff_token, sample_client):
        """Test listing all clients including inactive."""
        response = client.get(
            "/api/clients?active=false",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_get_client(self, client, db, staff_user, staff_token, sample_client):
        """Test getting a specific client."""
        response = client.get(
            f"/api/clients/{sample_client.id}",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["client"]["name"] == "Test Corp"

    def test_get_client_not_found(self, client, db, staff_user, staff_token):
        """Test getting a non-existent client."""
        response = client.get(
            "/api/clients/9999",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 404

    def test_create_client(self, client, db, admin_user, admin_token):
        """Test creating a new client."""
        response = client.post(
            "/api/clients",
            data=json.dumps({
                "name": "New Corp",
                "code": "NCORP",
                "industry": "Banking",
                "contact_person": "Jane",
                "contact_email": "jane@newcorp.com",
                "contact_phone": "+231-555-0123",
                "address": "123 Main St",
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["client"]["code"] == "NCORP"

    def test_create_client_missing_name(self, client, db, admin_user, admin_token):
        """Test creating client without a name."""
        response = client.post(
            "/api/clients",
            data=json.dumps({"code": "X"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_create_client_invalid_code(self, client, db, admin_user, admin_token):
        """Test creating client with invalid code."""
        response = client.post(
            "/api/clients",
            data=json.dumps({"name": "Test", "code": "AB"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_create_client_duplicate_code(self, client, db, admin_user, admin_token, sample_client):
        """Test creating client with duplicate code."""
        response = client.post(
            "/api/clients",
            data=json.dumps({"name": "Dup", "code": "TCORP"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 409

    def test_create_client_staff_forbidden(self, client, db, staff_user, staff_token):
        """Test that staff cannot create clients."""
        response = client.post(
            "/api/clients",
            data=json.dumps({"name": "Test", "code": "TST01"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 403

    def test_update_client(self, client, db, admin_user, admin_token, sample_client):
        """Test updating a client."""
        response = client.put(
            f"/api/clients/{sample_client.id}",
            data=json.dumps({
                "name": "Updated Corp",
                "industry": "Technology",
                "is_active": False,
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["client"]["name"] == "Updated Corp"
        assert data["client"]["is_active"] is False

    def test_update_client_not_found(self, client, db, admin_user, admin_token):
        """Test updating non-existent client."""
        response = client.put(
            "/api/clients/9999",
            data=json.dumps({"name": "X"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

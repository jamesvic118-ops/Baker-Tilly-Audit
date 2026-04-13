"""Tests for user management routes."""
import json


class TestUserRoutes:
    """Test suite for user API endpoints."""

    def test_list_users_as_admin(self, client, db, admin_user, admin_token):
        """Test listing all users as admin."""
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        users = response.get_json()["users"]
        assert len(users) >= 1

    def test_list_users_as_staff(self, client, db, admin_user, staff_user, staff_token):
        """Test listing users as staff (only active)."""
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_get_user(self, client, db, admin_user, admin_token, staff_user):
        """Test getting a specific user."""
        response = client.get(
            f"/api/users/{staff_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["user"]["email"] == "staff@test.com"

    def test_get_user_not_found(self, client, db, admin_user, admin_token):
        """Test getting a non-existent user."""
        response = client.get(
            "/api/users/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_create_user(self, client, db, admin_user, admin_token):
        """Test creating a new user as admin."""
        response = client.post(
            "/api/users",
            data=json.dumps({
                "email": "newuser@test.com",
                "password": "password123",
                "first_name": "New",
                "last_name": "Employee",
                "role": "staff",
                "department": "Tax",
                "employee_id": "EMP001",
                "hourly_rate": 50.0,
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["user"]["email"] == "newuser@test.com"
        assert data["user"]["role"] == "staff"

    def test_create_user_duplicate_email(self, client, db, admin_user, admin_token):
        """Test creating user with duplicate email."""
        response = client.post(
            "/api/users",
            data=json.dumps({
                "email": "admin@test.com",
                "password": "password123",
                "first_name": "Dup",
                "last_name": "User",
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 409

    def test_create_user_invalid_role(self, client, db, admin_user, admin_token):
        """Test creating user with invalid role."""
        response = client.post(
            "/api/users",
            data=json.dumps({
                "email": "bad@test.com",
                "password": "password123",
                "first_name": "Bad",
                "last_name": "Role",
                "role": "superuser",
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_create_user_missing_names(self, client, db, admin_user, admin_token):
        """Test creating user without names."""
        response = client.post(
            "/api/users",
            data=json.dumps({
                "email": "noname@test.com",
                "password": "password123",
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_create_user_staff_forbidden(self, client, db, staff_user, staff_token):
        """Test that staff cannot create users."""
        response = client.post(
            "/api/users",
            data=json.dumps({
                "email": "x@test.com",
                "password": "password123",
                "first_name": "X",
                "last_name": "Y",
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 403

    def test_update_user(self, client, db, admin_user, admin_token, staff_user):
        """Test updating a user as admin."""
        response = client.put(
            f"/api/users/{staff_user.id}",
            data=json.dumps({
                "first_name": "Updated",
                "role": "manager",
                "department": "Advisory",
                "hourly_rate": 75.0,
                "is_active": False,
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["user"]["first_name"] == "Updated"
        assert data["user"]["role"] == "manager"

    def test_update_user_not_found(self, client, db, admin_user, admin_token):
        """Test updating a non-existent user."""
        response = client.put(
            "/api/users/9999",
            data=json.dumps({"first_name": "X"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_update_user_invalid_role(self, client, db, admin_user, admin_token, staff_user):
        """Test updating user with invalid role."""
        response = client.put(
            f"/api/users/{staff_user.id}",
            data=json.dumps({"role": "invalid"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

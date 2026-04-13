"""Tests for authentication routes."""
import json


class TestAuthRoutes:
    """Test suite for auth API endpoints."""

    def test_login_success(self, client, admin_user):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            data=json.dumps({"email": "admin@test.com", "password": "password123"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "token" in data
        assert data["user"]["email"] == "admin@test.com"

    def test_login_wrong_password(self, client, admin_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/auth/login",
            data=json.dumps({"email": "admin@test.com", "password": "wrong"}),
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client, db):
        """Test login with non-existent user."""
        response = client.post(
            "/api/auth/login",
            data=json.dumps({"email": "none@test.com", "password": "password123"}),
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_login_missing_fields(self, client, db):
        """Test login with missing fields."""
        response = client.post(
            "/api/auth/login",
            data=json.dumps({"email": ""}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_register_success(self, client, db):
        """Test successful registration."""
        response = client.post(
            "/api/auth/register",
            data=json.dumps({
                "email": "new@test.com",
                "password": "password123",
                "first_name": "New",
                "last_name": "User",
            }),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "token" in data
        assert data["user"]["email"] == "new@test.com"
        assert data["user"]["role"] == "staff"

    def test_register_duplicate_email(self, client, admin_user):
        """Test registration with existing email."""
        response = client.post(
            "/api/auth/register",
            data=json.dumps({
                "email": "admin@test.com",
                "password": "password123",
                "first_name": "Dup",
                "last_name": "User",
            }),
            content_type="application/json",
        )
        assert response.status_code == 409

    def test_register_weak_password(self, client, db):
        """Test registration with weak password."""
        response = client.post(
            "/api/auth/register",
            data=json.dumps({
                "email": "weak@test.com",
                "password": "123",
                "first_name": "Weak",
                "last_name": "Pass",
            }),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_get_current_user(self, client, admin_user, admin_token):
        """Test getting current user profile."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["user"]["email"] == "admin@test.com"

    def test_get_current_user_no_token(self, client, db):
        """Test getting current user without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_change_password(self, client, admin_user, admin_token):
        """Test changing password."""
        response = client.put(
            "/api/auth/change-password",
            data=json.dumps({
                "current_password": "password123",
                "new_password": "newpassword123",
            }),
            content_type="application/json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

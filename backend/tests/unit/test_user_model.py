"""Tests for the User model."""
import pytest
from app.models.user import User


class TestUserModel:
    """Test suite for the User model."""

    def test_create_user(self, db):
        """Test creating a new user."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="staff",
            department="Audit",
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == "staff"

    def test_password_hashing(self, db):
        """Test password hashing and verification."""
        user = User(email="hash@test.com", first_name="Hash", last_name="Test", role="staff")
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "secret123"
        assert user.check_password("secret123") is True
        assert user.check_password("wrong") is False

    def test_full_name(self, db):
        """Test the full_name property."""
        user = User(email="fn@test.com", first_name="John", last_name="Doe", role="staff")
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()

        assert user.full_name == "John Doe"

    def test_is_admin(self, admin_user):
        """Test the is_admin method."""
        assert admin_user.is_admin() is True
        assert admin_user.is_manager() is False

    def test_is_manager(self, manager_user):
        """Test the is_manager method."""
        assert manager_user.is_manager() is True
        assert manager_user.is_admin() is False

    def test_is_staff(self, staff_user):
        """Test staff role methods."""
        assert staff_user.is_admin() is False
        assert staff_user.is_manager() is False

    def test_to_dict(self, admin_user):
        """Test serialization to dictionary."""
        d = admin_user.to_dict()
        assert d["email"] == "admin@test.com"
        assert d["first_name"] == "Admin"
        assert d["last_name"] == "Tester"
        assert d["role"] == "admin"
        assert d["full_name"] == "Admin Tester"
        assert "password_hash" not in d

    def test_unique_email(self, db):
        """Test that duplicate emails are rejected."""
        user1 = User(email="dup@test.com", first_name="A", last_name="B", role="staff")
        user1.set_password("pass")
        db.session.add(user1)
        db.session.commit()

        user2 = User(email="dup@test.com", first_name="C", last_name="D", role="staff")
        user2.set_password("pass")
        db.session.add(user2)
        with pytest.raises(Exception):
            db.session.commit()

"""Tests for validation utilities."""
from app.utils.validators import (
    validate_email,
    validate_required_string,
    validate_password,
    validate_role,
    validate_positive_number,
)


class TestValidateEmail:
    """Tests for validate_email."""

    def test_valid_email(self):
        valid, result = validate_email("user@example.com")
        assert valid is True
        assert result == "user@example.com"

    def test_valid_email_uppercase(self):
        valid, result = validate_email("USER@Example.COM")
        assert valid is True
        assert result == "user@example.com"

    def test_valid_email_with_dots(self):
        valid, result = validate_email("first.last@example.com")
        assert valid is True

    def test_empty_email(self):
        valid, result = validate_email("")
        assert valid is False

    def test_none_email(self):
        valid, result = validate_email(None)
        assert valid is False

    def test_invalid_format(self):
        valid, result = validate_email("not-an-email")
        assert valid is False

    def test_missing_domain(self):
        valid, result = validate_email("user@")
        assert valid is False

    def test_spaces_trimmed(self):
        valid, result = validate_email("  user@test.com  ")
        assert valid is True
        assert result == "user@test.com"


class TestValidateRequiredString:
    """Tests for validate_required_string."""

    def test_valid_string(self):
        valid, result = validate_required_string("hello", "Name")
        assert valid is True
        assert result == "hello"

    def test_empty_string(self):
        valid, result = validate_required_string("", "Name")
        assert valid is False
        assert "required" in result.lower()

    def test_none_value(self):
        valid, result = validate_required_string(None, "Name")
        assert valid is False

    def test_whitespace_only(self):
        valid, result = validate_required_string("   ", "Name")
        assert valid is False

    def test_min_length_not_met(self):
        valid, result = validate_required_string("ab", "Name", min_length=3)
        assert valid is False
        assert "at least 3" in result

    def test_max_length_exceeded(self):
        valid, result = validate_required_string("a" * 10, "Name", max_length=5)
        assert valid is False
        assert "at most 5" in result

    def test_trimming(self):
        valid, result = validate_required_string("  trimmed  ", "Name")
        assert valid is True
        assert result == "trimmed"


class TestValidatePassword:
    """Tests for validate_password."""

    def test_valid_password(self):
        valid, result = validate_password("password123")
        assert valid is True

    def test_empty_password(self):
        valid, result = validate_password("")
        assert valid is False

    def test_none_password(self):
        valid, result = validate_password(None)
        assert valid is False

    def test_too_short(self):
        valid, result = validate_password("123")
        assert valid is False
        assert "at least 6" in result

    def test_too_long(self):
        valid, result = validate_password("a" * 129)
        assert valid is False
        assert "at most 128" in result

    def test_exactly_min_length(self):
        valid, result = validate_password("123456")
        assert valid is True


class TestValidateRole:
    """Tests for validate_role."""

    def test_valid_admin(self):
        valid, result = validate_role("admin")
        assert valid is True
        assert result == "admin"

    def test_valid_manager(self):
        valid, result = validate_role("manager")
        assert valid is True

    def test_valid_staff(self):
        valid, result = validate_role("staff")
        assert valid is True

    def test_uppercase_role(self):
        valid, result = validate_role("ADMIN")
        assert valid is True
        assert result == "admin"

    def test_invalid_role(self):
        valid, result = validate_role("superuser")
        assert valid is False

    def test_none_role(self):
        valid, result = validate_role(None)
        assert valid is False

    def test_empty_role(self):
        valid, result = validate_role("")
        assert valid is False


class TestValidatePositiveNumber:
    """Tests for validate_positive_number."""

    def test_valid_number(self):
        valid, result = validate_positive_number(10.5, "Rate")
        assert valid is True
        assert result == 10.5

    def test_zero(self):
        valid, result = validate_positive_number(0, "Rate")
        assert valid is True
        assert result == 0.0

    def test_negative_number(self):
        valid, result = validate_positive_number(-5, "Rate")
        assert valid is False
        assert "positive" in result.lower()

    def test_none_value(self):
        valid, result = validate_positive_number(None, "Rate")
        assert valid is False

    def test_string_number(self):
        valid, result = validate_positive_number("42.5", "Rate")
        assert valid is True
        assert result == 42.5

    def test_invalid_string(self):
        valid, result = validate_positive_number("abc", "Rate")
        assert valid is False

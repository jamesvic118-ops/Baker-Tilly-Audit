"""Validation utility functions."""
import re


def validate_email(email):
    """Validate email format."""
    if not email or not email.strip():
        return False, "Email is required"
    email = email.strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, email


def validate_required_string(value, field_name, min_length=1, max_length=255):
    """Validate a required string field."""
    if not value or not str(value).strip():
        return False, f"{field_name} is required"
    value = str(value).strip()
    if len(value) < min_length:
        return False, f"{field_name} must be at least {min_length} characters"
    if len(value) > max_length:
        return False, f"{field_name} must be at most {max_length} characters"
    return True, value


def validate_password(password):
    """Validate password strength."""
    if not password:
        return False, "Password is required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 128:
        return False, "Password must be at most 128 characters"
    return True, password


def validate_role(role):
    """Validate user role."""
    valid_roles = ("admin", "manager", "staff")
    if not role or role.lower() not in valid_roles:
        return False, f"Role must be one of: {', '.join(valid_roles)}"
    return True, role.lower()


def validate_positive_number(value, field_name):
    """Validate that a value is a positive number."""
    if value is None:
        return False, f"{field_name} is required"
    try:
        value = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"
    if value < 0:
        return False, f"{field_name} must be positive"
    return True, value

"""User management routes."""
from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.utils.auth import token_required, admin_required
from app.utils.validators import validate_email, validate_password, validate_role

user_bp = Blueprint("user", __name__)


@user_bp.route("", methods=["GET"])
@token_required
def list_users(current_user):
    """List all users (admin sees all, others see active only)."""
    if current_user.is_admin():
        users = User.query.order_by(User.last_name.asc()).all()
    else:
        users = User.query.filter_by(is_active=True).order_by(User.last_name.asc()).all()
    return jsonify({"users": [u.to_dict() for u in users]}), 200


@user_bp.route("/<int:user_id>", methods=["GET"])
@token_required
def get_user(current_user, user_id):
    """Get a specific user's profile."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


@user_bp.route("", methods=["POST"])
@admin_required
def create_user(current_user):
    """Create a new user (admin only)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Validate email
    valid, result = validate_email(data.get("email"))
    if not valid:
        return jsonify({"error": result}), 400
    email = result

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    # Validate password
    valid, result = validate_password(data.get("password"))
    if not valid:
        return jsonify({"error": result}), 400

    # Validate role
    valid, result = validate_role(data.get("role", "staff"))
    if not valid:
        return jsonify({"error": result}), 400
    role = result

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    if not first_name or not last_name:
        return jsonify({"error": "First name and last name are required"}), 400

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        department=data.get("department", "").strip() or None,
        employee_id=data.get("employee_id", "").strip() or None,
        hourly_rate=float(data.get("hourly_rate", 0)),
        is_active=True,
    )
    user.set_password(data.get("password"))

    db.session.add(user)
    db.session.commit()

    return jsonify({"user": user.to_dict(), "message": "User created"}), 201


@user_bp.route("/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(current_user, user_id):
    """Update a user (admin only)."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    if "first_name" in data:
        user.first_name = data["first_name"].strip()
    if "last_name" in data:
        user.last_name = data["last_name"].strip()
    if "role" in data:
        valid, result = validate_role(data["role"])
        if not valid:
            return jsonify({"error": result}), 400
        user.role = result
    if "department" in data:
        user.department = data["department"].strip() or None
    if "employee_id" in data:
        user.employee_id = data["employee_id"].strip() or None
    if "hourly_rate" in data:
        user.hourly_rate = float(data["hourly_rate"])
    if "is_active" in data:
        user.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify({"user": user.to_dict(), "message": "User updated"}), 200

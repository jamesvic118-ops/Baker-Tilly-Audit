"""Authentication routes."""
from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.utils.auth import generate_token, token_required
from app.utils.validators import validate_email, validate_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate a user and return a JWT token."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    token = generate_token(user.id)
    return jsonify({
        "token": token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Validate email
    valid, result = validate_email(data.get("email"))
    if not valid:
        return jsonify({"error": result}), 400
    email = result

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    # Validate password
    valid, result = validate_password(data.get("password"))
    if not valid:
        return jsonify({"error": result}), 400

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    if not first_name or not last_name:
        return jsonify({"error": "First name and last name are required"}), 400

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role="staff",
        department=data.get("department", "").strip() or None,
    )
    user.set_password(data.get("password"))

    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        "token": token,
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    """Get the currently authenticated user's profile."""
    return jsonify({"user": current_user.to_dict()}), 200


@auth_bp.route("/change-password", methods=["PUT"])
@token_required
def change_password(current_user):
    """Change the current user's password."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 400

    valid, result = validate_password(new_password)
    if not valid:
        return jsonify({"error": result}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200

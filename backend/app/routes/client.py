"""Client management routes."""
from flask import Blueprint, request, jsonify
from app import db
from app.models.client import Client
from app.utils.auth import token_required, manager_or_admin_required

client_bp = Blueprint("client", __name__)


@client_bp.route("", methods=["GET"])
@token_required
def list_clients(current_user):
    """List all clients."""
    active_only = request.args.get("active", "true").lower() == "true"
    query = Client.query
    if active_only:
        query = query.filter_by(is_active=True)
    clients = query.order_by(Client.name.asc()).all()
    return jsonify({"clients": [c.to_dict() for c in clients]}), 200


@client_bp.route("/<int:client_id>", methods=["GET"])
@token_required
def get_client(current_user, client_id):
    """Get a specific client."""
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify({"client": client.to_dict()}), 200


@client_bp.route("", methods=["POST"])
@manager_or_admin_required
def create_client(current_user):
    """Create a new client."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Client name is required"}), 400

    # Validate code
    valid, result = Client.validate_code(data.get("code", ""))
    if not valid:
        return jsonify({"error": result}), 400
    code = result

    if Client.query.filter_by(code=code).first():
        return jsonify({"error": "Client code already exists"}), 409

    client = Client(
        name=name,
        code=code,
        industry=data.get("industry", "").strip() or None,
        contact_person=data.get("contact_person", "").strip() or None,
        contact_email=data.get("contact_email", "").strip() or None,
        contact_phone=data.get("contact_phone", "").strip() or None,
        address=data.get("address", "").strip() or None,
    )

    db.session.add(client)
    db.session.commit()

    return jsonify({"client": client.to_dict(), "message": "Client created"}), 201


@client_bp.route("/<int:client_id>", methods=["PUT"])
@manager_or_admin_required
def update_client(current_user, client_id):
    """Update a client."""
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    if "name" in data:
        client.name = data["name"].strip()
    if "industry" in data:
        client.industry = data["industry"].strip() or None
    if "contact_person" in data:
        client.contact_person = data["contact_person"].strip() or None
    if "contact_email" in data:
        client.contact_email = data["contact_email"].strip() or None
    if "contact_phone" in data:
        client.contact_phone = data["contact_phone"].strip() or None
    if "address" in data:
        client.address = data["address"].strip() or None
    if "is_active" in data:
        client.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify({"client": client.to_dict(), "message": "Client updated"}), 200

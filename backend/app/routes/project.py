"""Project management routes."""
from datetime import date
from flask import Blueprint, request, jsonify
from app import db
from app.models.project import Project
from app.models.client import Client
from app.utils.auth import token_required, manager_or_admin_required

project_bp = Blueprint("project", __name__)


@project_bp.route("", methods=["GET"])
@token_required
def list_projects(current_user):
    """List all active projects."""
    status_filter = request.args.get("status", "active")
    client_id = request.args.get("client_id")

    query = Project.query
    if status_filter != "all":
        query = query.filter_by(status=status_filter)
    if client_id:
        query = query.filter_by(client_id=int(client_id))

    projects = query.order_by(Project.name.asc()).all()
    return jsonify({"projects": [p.to_dict() for p in projects]}), 200


@project_bp.route("/<int:project_id>", methods=["GET"])
@token_required
def get_project(current_user, project_id):
    """Get a specific project."""
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify({"project": project.to_dict()}), 200


@project_bp.route("", methods=["POST"])
@manager_or_admin_required
def create_project(current_user):
    """Create a new project."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    name = data.get("name", "").strip()
    code = data.get("code", "").strip().upper()
    client_id = data.get("client_id")

    if not name:
        return jsonify({"error": "Project name is required"}), 400
    if not code:
        return jsonify({"error": "Project code is required"}), 400
    if not client_id:
        return jsonify({"error": "Client is required"}), 400

    if Project.query.filter_by(code=code).first():
        return jsonify({"error": "Project code already exists"}), 409

    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    project = Project(
        name=name,
        code=code,
        description=data.get("description", "").strip() or None,
        client_id=client_id,
        manager_id=data.get("manager_id") or current_user.id,
        status=data.get("status", "active"),
        budget_hours=data.get("budget_hours", 0),
        engagement_type=data.get("engagement_type"),
        is_billable=data.get("is_billable", True),
    )

    if data.get("start_date"):
        project.start_date = date.fromisoformat(data["start_date"])
    if data.get("end_date"):
        project.end_date = date.fromisoformat(data["end_date"])

    db.session.add(project)
    db.session.commit()

    return jsonify({"project": project.to_dict(), "message": "Project created"}), 201


@project_bp.route("/<int:project_id>", methods=["PUT"])
@manager_or_admin_required
def update_project(current_user, project_id):
    """Update a project."""
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    if "name" in data:
        project.name = data["name"].strip()
    if "description" in data:
        project.description = data["description"].strip() or None
    if "status" in data:
        if data["status"] not in Project.VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(Project.VALID_STATUSES)}"}), 400
        project.status = data["status"]
    if "budget_hours" in data:
        project.budget_hours = float(data["budget_hours"])
    if "manager_id" in data:
        project.manager_id = data["manager_id"]
    if "engagement_type" in data:
        project.engagement_type = data["engagement_type"]
    if "is_billable" in data:
        project.is_billable = data["is_billable"]
    if "start_date" in data:
        project.start_date = date.fromisoformat(data["start_date"]) if data["start_date"] else None
    if "end_date" in data:
        project.end_date = date.fromisoformat(data["end_date"]) if data["end_date"] else None

    db.session.commit()
    return jsonify({"project": project.to_dict(), "message": "Project updated"}), 200

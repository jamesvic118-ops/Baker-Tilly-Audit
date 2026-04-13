"""Timesheet entry routes."""
from datetime import date
from flask import Blueprint, request, jsonify
from app.models.timesheet import TimesheetEntry
from app.services.timesheet_service import TimesheetService
from app.utils.auth import token_required

timesheet_bp = Blueprint("timesheet", __name__)


@timesheet_bp.route("", methods=["GET"])
@token_required
def list_entries(current_user):
    """List timesheet entries for the current user."""
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    status_filter = request.args.get("status")

    query = TimesheetEntry.query.filter_by(user_id=current_user.id)

    if start:
        query = query.filter(TimesheetEntry.date >= date.fromisoformat(start))
    if end:
        query = query.filter(TimesheetEntry.date <= date.fromisoformat(end))
    if status_filter:
        query = query.filter(TimesheetEntry.status == status_filter)

    entries = query.order_by(TimesheetEntry.date.desc()).all()
    return jsonify({"entries": [e.to_dict() for e in entries]}), 200


@timesheet_bp.route("", methods=["POST"])
@token_required
def create_entry(current_user):
    """Create a new timesheet entry."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    entry, message = TimesheetService.create_entry(
        user_id=current_user.id,
        project_id=data.get("project_id"),
        entry_date=data.get("date"),
        hours=data.get("hours"),
        description=data.get("description"),
        is_billable=data.get("is_billable", True),
    )

    if not entry:
        return jsonify({"error": message}), 400

    return jsonify({"entry": entry.to_dict(), "message": message}), 201


@timesheet_bp.route("/<int:entry_id>", methods=["GET"])
@token_required
def get_entry(current_user, entry_id):
    """Get a specific timesheet entry."""
    entry = TimesheetEntry.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    if entry.user_id != current_user.id and not current_user.is_admin():
        return jsonify({"error": "Not authorized"}), 403
    return jsonify({"entry": entry.to_dict()}), 200


@timesheet_bp.route("/<int:entry_id>", methods=["PUT"])
@token_required
def update_entry(current_user, entry_id):
    """Update a timesheet entry."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    entry, message = TimesheetService.update_entry(entry_id, current_user.id, **data)
    if not entry:
        return jsonify({"error": message}), 400

    return jsonify({"entry": entry.to_dict(), "message": message}), 200


@timesheet_bp.route("/<int:entry_id>", methods=["DELETE"])
@token_required
def delete_entry(current_user, entry_id):
    """Delete a timesheet entry."""
    success, message = TimesheetService.delete_entry(entry_id, current_user.id)
    if not success:
        return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200


@timesheet_bp.route("/submit", methods=["POST"])
@token_required
def submit_entries(current_user):
    """Submit timesheet entries for approval."""
    data = request.get_json()
    if not data or "entry_ids" not in data:
        return jsonify({"error": "entry_ids are required"}), 400

    submitted, result = TimesheetService.submit_entries(
        current_user.id, data["entry_ids"]
    )
    if isinstance(result, list) and result:
        return jsonify({
            "submitted": len(submitted),
            "errors": result,
        }), 207
    return jsonify({
        "submitted": len(submitted),
        "message": "All entries submitted for approval",
    }), 200

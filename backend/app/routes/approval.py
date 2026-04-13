"""Approval workflow routes."""
from flask import Blueprint, request, jsonify
from app import db
from app.models.timesheet import TimesheetEntry
from app.services.timesheet_service import TimesheetService
from app.utils.auth import token_required, manager_or_admin_required

approval_bp = Blueprint("approval", __name__)


@approval_bp.route("/pending", methods=["GET"])
@manager_or_admin_required
def list_pending(current_user):
    """List all entries pending approval."""
    if current_user.is_admin():
        entries = TimesheetService.get_pending_approvals()
    else:
        entries = TimesheetService.get_pending_approvals(manager_id=current_user.id)
    return jsonify({"entries": [e.to_dict() for e in entries]}), 200


@approval_bp.route("/approve/<int:entry_id>", methods=["POST"])
@manager_or_admin_required
def approve_entry(current_user, entry_id):
    """Approve a timesheet entry."""
    entry = TimesheetEntry.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    success, message = entry.approve(current_user.id)
    if not success:
        return jsonify({"error": message}), 400

    db.session.commit()
    return jsonify({"entry": entry.to_dict(), "message": message}), 200


@approval_bp.route("/reject/<int:entry_id>", methods=["POST"])
@manager_or_admin_required
def reject_entry(current_user, entry_id):
    """Reject a timesheet entry."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    entry = TimesheetEntry.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    reason = data.get("reason", "").strip()
    success, message = entry.reject(current_user.id, reason)
    if not success:
        return jsonify({"error": message}), 400

    db.session.commit()
    return jsonify({"entry": entry.to_dict(), "message": message}), 200


@approval_bp.route("/batch-approve", methods=["POST"])
@manager_or_admin_required
def batch_approve(current_user):
    """Approve multiple timesheet entries at once."""
    data = request.get_json()
    if not data or "entry_ids" not in data:
        return jsonify({"error": "entry_ids are required"}), 400

    approved = []
    errors = []
    for entry_id in data["entry_ids"]:
        entry = TimesheetEntry.query.get(entry_id)
        if not entry:
            errors.append(f"Entry {entry_id}: not found")
            continue
        success, message = entry.approve(current_user.id)
        if success:
            approved.append(entry_id)
        else:
            errors.append(f"Entry {entry_id}: {message}")

    db.session.commit()
    return jsonify({
        "approved": approved,
        "errors": errors,
        "message": f"{len(approved)} entries approved",
    }), 200

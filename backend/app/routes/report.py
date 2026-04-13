"""Report routes."""
from datetime import date
from flask import Blueprint, request, jsonify
from app.services.report_service import ReportService
from app.utils.auth import token_required, manager_or_admin_required
from app.utils.date_helpers import get_week_range, get_month_range

report_bp = Blueprint("report", __name__)


@report_bp.route("/my-summary", methods=["GET"])
@token_required
def my_summary(current_user):
    """Get the current user's timesheet summary."""
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    if start and end:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    else:
        start_date, end_date = get_week_range()

    summary = ReportService.get_user_summary(current_user.id, start_date, end_date)
    return jsonify({"summary": summary}), 200


@report_bp.route("/user/<int:user_id>", methods=["GET"])
@manager_or_admin_required
def user_summary(current_user, user_id):
    """Get a specific user's timesheet summary (manager/admin only)."""
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    if start and end:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    else:
        start_date, end_date = get_week_range()

    summary = ReportService.get_user_summary(user_id, start_date, end_date)
    return jsonify({"summary": summary}), 200


@report_bp.route("/project/<int:project_id>", methods=["GET"])
@token_required
def project_summary(current_user, project_id):
    """Get a project's timesheet summary."""
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    start_date = date.fromisoformat(start) if start else None
    end_date = date.fromisoformat(end) if end else None

    summary = ReportService.get_project_summary(project_id, start_date, end_date)
    return jsonify({"summary": summary}), 200


@report_bp.route("/team", methods=["GET"])
@manager_or_admin_required
def team_summary(current_user):
    """Get team-wide timesheet summary (manager/admin only)."""
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    if start and end:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    else:
        start_date, end_date = get_month_range(date.today().year, date.today().month)

    summary = ReportService.get_team_summary(start_date, end_date)
    return jsonify({"summary": summary}), 200

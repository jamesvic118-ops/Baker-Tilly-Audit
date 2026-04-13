"""Report generation service."""
from datetime import date
from sqlalchemy import func
from app import db
from app.models.timesheet import TimesheetEntry
from app.models.project import Project
from app.models.client import Client
from app.models.user import User


class ReportService:
    """Service class for generating reports."""

    @staticmethod
    def get_user_summary(user_id, start_date, end_date):
        """Get a summary of hours for a user within a date range."""
        entries = (
            TimesheetEntry.query.filter(
                TimesheetEntry.user_id == user_id,
                TimesheetEntry.date >= start_date,
                TimesheetEntry.date <= end_date,
            )
            .all()
        )

        total_hours = sum(e.hours for e in entries)
        billable_hours = sum(e.hours for e in entries if e.is_billable)
        non_billable_hours = total_hours - billable_hours

        by_project = {}
        for entry in entries:
            project_name = entry.project.name if entry.project else "Unknown"
            if project_name not in by_project:
                by_project[project_name] = {"total": 0, "billable": 0, "non_billable": 0}
            by_project[project_name]["total"] += entry.hours
            if entry.is_billable:
                by_project[project_name]["billable"] += entry.hours
            else:
                by_project[project_name]["non_billable"] += entry.hours

        by_status = {}
        for entry in entries:
            status = entry.status
            by_status[status] = by_status.get(status, 0) + entry.hours

        return {
            "user_id": user_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_hours": round(total_hours, 2),
            "billable_hours": round(billable_hours, 2),
            "non_billable_hours": round(non_billable_hours, 2),
            "utilization_rate": (
                round((billable_hours / total_hours) * 100, 2) if total_hours > 0 else 0
            ),
            "by_project": by_project,
            "by_status": by_status,
            "entry_count": len(entries),
        }

    @staticmethod
    def get_project_summary(project_id, start_date=None, end_date=None):
        """Get a summary of hours for a project."""
        query = TimesheetEntry.query.filter(TimesheetEntry.project_id == project_id)
        if start_date:
            query = query.filter(TimesheetEntry.date >= start_date)
        if end_date:
            query = query.filter(TimesheetEntry.date <= end_date)

        entries = query.all()
        project = Project.query.get(project_id)

        total_hours = sum(e.hours for e in entries)
        billable_hours = sum(e.hours for e in entries if e.is_billable)

        by_user = {}
        for entry in entries:
            user_name = entry.user.full_name if entry.user else "Unknown"
            if user_name not in by_user:
                by_user[user_name] = 0
            by_user[user_name] += entry.hours

        return {
            "project_id": project_id,
            "project_name": project.name if project else "Unknown",
            "total_hours": round(total_hours, 2),
            "billable_hours": round(billable_hours, 2),
            "budget_hours": project.budget_hours if project else 0,
            "budget_utilization": project.budget_utilization if project else 0,
            "by_user": by_user,
            "entry_count": len(entries),
        }

    @staticmethod
    def get_team_summary(start_date, end_date):
        """Get a summary of hours for all team members."""
        results = (
            db.session.query(
                User.id,
                User.first_name,
                User.last_name,
                func.sum(TimesheetEntry.hours).label("total_hours"),
                func.sum(
                    db.case(
                        (TimesheetEntry.is_billable == True, TimesheetEntry.hours),  # noqa: E712
                        else_=0,
                    )
                ).label("billable_hours"),
                func.count(TimesheetEntry.id).label("entry_count"),
            )
            .join(TimesheetEntry, User.id == TimesheetEntry.user_id)
            .filter(
                TimesheetEntry.date >= start_date,
                TimesheetEntry.date <= end_date,
            )
            .group_by(User.id, User.first_name, User.last_name)
            .all()
        )

        team_data = []
        for row in results:
            total = float(row.total_hours or 0)
            billable = float(row.billable_hours or 0)
            team_data.append({
                "user_id": row.id,
                "name": f"{row.first_name} {row.last_name}",
                "total_hours": round(total, 2),
                "billable_hours": round(billable, 2),
                "non_billable_hours": round(total - billable, 2),
                "utilization_rate": round((billable / total) * 100, 2) if total > 0 else 0,
                "entry_count": row.entry_count,
            })

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "team": sorted(team_data, key=lambda x: x["total_hours"], reverse=True),
        }

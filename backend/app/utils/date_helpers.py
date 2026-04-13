"""Date and time utility functions."""
from datetime import date, timedelta


def get_week_range(target_date=None):
    """Get the start (Monday) and end (Sunday) dates of the week containing target_date."""
    if target_date is None:
        target_date = date.today()
    start = target_date - timedelta(days=target_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_month_range(year, month):
    """Get the start and end dates of a given month."""
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def format_hours(hours):
    """Format hours as HH:MM string."""
    if hours is None:
        return "0:00"
    whole_hours = int(hours)
    minutes = int((hours - whole_hours) * 60)
    return f"{whole_hours}:{minutes:02d}"


def calculate_working_days(start_date, end_date):
    """Calculate the number of working days (Mon-Fri) between two dates."""
    if start_date > end_date:
        return 0
    working_days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Monday = 0, Friday = 4
            working_days += 1
        current += timedelta(days=1)
    return working_days


def is_weekend(target_date):
    """Check if a date falls on a weekend."""
    return target_date.weekday() >= 5

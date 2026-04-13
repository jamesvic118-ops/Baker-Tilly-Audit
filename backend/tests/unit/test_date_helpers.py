"""Tests for date helper utilities."""
from datetime import date, timedelta
from app.utils.date_helpers import (
    get_week_range,
    get_month_range,
    format_hours,
    calculate_working_days,
    is_weekend,
)


class TestGetWeekRange:
    """Tests for get_week_range."""

    def test_returns_monday_to_sunday(self):
        """Test that week range starts on Monday and ends on Sunday."""
        # Use a known Wednesday: 2024-01-10
        target = date(2024, 1, 10)
        start, end = get_week_range(target)
        assert start == date(2024, 1, 8)  # Monday
        assert end == date(2024, 1, 14)  # Sunday

    def test_monday_input(self):
        """Test with a Monday as input."""
        target = date(2024, 1, 8)
        start, end = get_week_range(target)
        assert start == date(2024, 1, 8)
        assert end == date(2024, 1, 14)

    def test_sunday_input(self):
        """Test with a Sunday as input."""
        target = date(2024, 1, 14)
        start, end = get_week_range(target)
        assert start == date(2024, 1, 8)
        assert end == date(2024, 1, 14)

    def test_default_today(self):
        """Test default is current week."""
        start, end = get_week_range()
        today = date.today()
        assert start <= today <= end
        assert start.weekday() == 0  # Monday
        assert end.weekday() == 6  # Sunday


class TestGetMonthRange:
    """Tests for get_month_range."""

    def test_january(self):
        """Test January range."""
        start, end = get_month_range(2024, 1)
        assert start == date(2024, 1, 1)
        assert end == date(2024, 1, 31)

    def test_february_leap_year(self):
        """Test February in a leap year."""
        start, end = get_month_range(2024, 2)
        assert start == date(2024, 2, 1)
        assert end == date(2024, 2, 29)

    def test_february_non_leap_year(self):
        """Test February in a non-leap year."""
        start, end = get_month_range(2023, 2)
        assert start == date(2023, 2, 1)
        assert end == date(2023, 2, 28)

    def test_december(self):
        """Test December range (edge case for year boundary)."""
        start, end = get_month_range(2024, 12)
        assert start == date(2024, 12, 1)
        assert end == date(2024, 12, 31)


class TestFormatHours:
    """Tests for format_hours."""

    def test_whole_hours(self):
        """Test formatting whole hours."""
        assert format_hours(8) == "8:00"

    def test_half_hour(self):
        """Test formatting half hours."""
        assert format_hours(4.5) == "4:30"

    def test_quarter_hour(self):
        """Test formatting quarter hours."""
        assert format_hours(2.25) == "2:15"

    def test_zero_hours(self):
        """Test formatting zero hours."""
        assert format_hours(0) == "0:00"

    def test_none_hours(self):
        """Test formatting None."""
        assert format_hours(None) == "0:00"


class TestCalculateWorkingDays:
    """Tests for calculate_working_days."""

    def test_full_week(self):
        """Test a full Monday-Friday week."""
        start = date(2024, 1, 8)  # Monday
        end = date(2024, 1, 12)  # Friday
        assert calculate_working_days(start, end) == 5

    def test_includes_weekend(self):
        """Test range that includes weekend days."""
        start = date(2024, 1, 8)  # Monday
        end = date(2024, 1, 14)  # Sunday
        assert calculate_working_days(start, end) == 5

    def test_single_weekday(self):
        """Test a single weekday."""
        target = date(2024, 1, 10)  # Wednesday
        assert calculate_working_days(target, target) == 1

    def test_single_weekend_day(self):
        """Test a single weekend day."""
        target = date(2024, 1, 13)  # Saturday
        assert calculate_working_days(target, target) == 0

    def test_start_after_end(self):
        """Test when start is after end."""
        assert calculate_working_days(date(2024, 1, 15), date(2024, 1, 10)) == 0


class TestIsWeekend:
    """Tests for is_weekend."""

    def test_saturday(self):
        """Test Saturday is weekend."""
        assert is_weekend(date(2024, 1, 13)) is True

    def test_sunday(self):
        """Test Sunday is weekend."""
        assert is_weekend(date(2024, 1, 14)) is True

    def test_monday(self):
        """Test Monday is not weekend."""
        assert is_weekend(date(2024, 1, 8)) is False

    def test_friday(self):
        """Test Friday is not weekend."""
        assert is_weekend(date(2024, 1, 12)) is False

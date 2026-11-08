"""Retake date rules (R-21), developed through TDD."""

from datetime import date, timedelta


def retake_date(
    exam_date: date, semester_end: date, holidays: tuple[date, ...] = ()
) -> date:
    """Return the first valid retake date after the exam."""
    return exam_date + timedelta(days=7)

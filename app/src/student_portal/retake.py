"""Retake date rules (R-21), developed through TDD."""

from datetime import date, timedelta


def retake_date(
    exam_date: date, semester_end: date, holidays: tuple[date, ...] = ()
) -> date:
    """Return the first valid retake date after the exam."""
    candidate = exam_date + timedelta(days=7)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    if candidate in holidays:
        candidate += timedelta(days=1)
    return candidate

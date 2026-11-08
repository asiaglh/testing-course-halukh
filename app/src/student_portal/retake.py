"""Retake date rules (R-21), developed through TDD."""

from datetime import date, timedelta


class NoRetakeDateError(ValueError):
    """No valid retake day exists within the semester."""


def retake_date(
    exam_date: date, semester_end: date, holidays: tuple[date, ...] = ()
) -> date:
    """Return the first valid retake date after the exam."""
    candidate = exam_date + timedelta(days=7)
    while candidate.weekday() >= 5 or candidate in holidays:
        candidate += timedelta(days=1)
    if candidate > semester_end:
        raise NoRetakeDateError(f"No retake date before semester end {semester_end}")
    return candidate

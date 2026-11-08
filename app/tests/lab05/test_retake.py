"""R-21 retake date, grown one behavior at a time with TDD."""

from datetime import date

from student_portal.retake import retake_date


def test_monday_exam_has_monday_retake_after_seven_days():
    exam = date(2026, 11, 2)
    semester_end = date(2026, 11, 30)

    actual = retake_date(exam, semester_end)

    assert actual == date(2026, 11, 9)


def test_tuesday_exam_triangulates_seven_day_rule():
    exam = date(2026, 11, 3)
    semester_end = date(2026, 11, 30)

    actual = retake_date(exam, semester_end)

    assert actual == date(2026, 11, 10)

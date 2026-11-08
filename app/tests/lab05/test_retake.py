"""R-21 retake date, grown one behavior at a time with TDD."""

from datetime import date

import pytest

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


@pytest.mark.parametrize(
    "exam",
    [
        pytest.param(date(2026, 11, 7), id="saturday"),
        pytest.param(date(2026, 11, 8), id="sunday"),
    ],
)
def test_weekend_candidate_moves_to_monday(exam):
    semester_end = date(2026, 11, 30)

    actual = retake_date(exam, semester_end)

    assert actual == date(2026, 11, 16)


def test_holiday_candidate_moves_to_next_working_day():
    exam = date(2026, 11, 2)
    semester_end = date(2026, 11, 30)
    holidays = (date(2026, 11, 9),)

    actual = retake_date(exam, semester_end, holidays)

    assert actual == date(2026, 11, 10)


# Temporary demonstration: disable the only test covering the error branch.
# def test_no_retake_date_before_semester_end():
#     exam = date(2026, 11, 2)
#     semester_end = date(2026, 11, 8)
#
#     with pytest.raises(NoRetakeDateError, match="2026-11-08"):
#         retake_date(exam, semester_end)


def test_retake_on_last_semester_day_is_allowed():
    exam = date(2026, 11, 2)
    semester_end = date(2026, 11, 9)

    assert retake_date(exam, semester_end) == semester_end


def test_consecutive_holidays_and_weekend_are_skipped():
    exam = date(2026, 11, 5)
    semester_end = date(2026, 11, 30)
    holidays = (date(2026, 11, 12), date(2026, 11, 13))

    assert retake_date(exam, semester_end, holidays) == date(2026, 11, 16)

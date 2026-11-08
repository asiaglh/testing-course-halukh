"""Property based checks for R-17 scholarship and R-21 retake dates."""

from datetime import date, timedelta
from statistics import fmean

import pytest
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st

from student_portal.grades import Grade
from student_portal.people import Funding, Student
from student_portal.retake import NoRetakeDateError, retake_date
from student_portal.scholarship import Scholarship, scholarship

EXAM_DATES = st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 1))
SCHOLARSHIP_RANK = {
    Scholarship.NONE: 0,
    Scholarship.REGULAR: 1,
    Scholarship.INCREASED: 2,
}


def _student(scores: list[int]) -> Student:
    return Student(
        1,
        "Анна",
        "Галух",
        [
            Grade(f"Предмет {index}", score, date(2026, 10, 1))
            for index, score in enumerate(scores)
        ],
        funding=Funding.BUDGET,
    )


@settings(max_examples=150)
@given(
    exam_date=EXAM_DATES,
    semester_span=st.integers(min_value=0, max_value=40),
    holiday_offsets=st.frozensets(st.integers(0, 50), max_size=10),
)
def test_retake_matches_a_day_by_day_reference(
    exam_date: date, semester_span: int, holiday_offsets: frozenset[int]
):
    semester_end = exam_date + timedelta(days=semester_span)
    holidays = frozenset(
        exam_date + timedelta(days=offset) for offset in holiday_offsets
    )

    expected = None
    for offset in range(7, semester_span + 1):
        candidate = exam_date + timedelta(days=offset)
        if candidate.weekday() < 5 and candidate not in holidays:
            expected = candidate
            break

    if expected is None:
        with pytest.raises(NoRetakeDateError, match=str(semester_end)):
            retake_date(exam_date, semester_end, holidays)
    else:
        assert retake_date(exam_date, semester_end, holidays) == expected


@settings(max_examples=100)
@given(
    exam_date=EXAM_DATES,
    holiday_offsets=st.frozensets(st.integers(0, 40), max_size=10),
)
def test_extending_semester_does_not_move_an_existing_retake(
    exam_date: date, holiday_offsets: frozenset[int]
):
    holidays = frozenset(
        exam_date + timedelta(days=offset) for offset in holiday_offsets
    )
    original_end = exam_date + timedelta(days=30)
    extended_end = original_end + timedelta(days=30)

    assert retake_date(exam_date, original_end, holidays) == retake_date(
        exam_date, extended_end, holidays
    )


@settings(max_examples=150)
@given(
    scores=st.lists(st.integers(0, 100), min_size=1, max_size=8),
    replacement=st.integers(0, 100),
)
def test_improving_the_worst_grade_never_reduces_scholarship(
    scores: list[int], replacement: int
):
    improved = scores.copy()
    worst_index = improved.index(min(improved))
    improved[worst_index] = max(improved[worst_index], replacement)

    assert (
        SCHOLARSHIP_RANK[scholarship(_student(improved))]
        >= SCHOLARSHIP_RANK[scholarship(_student(scores))]
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект Р-17 #15: Fx і середнє >= 90",
)
@settings(max_examples=100)
@given(
    fx_score=st.integers(50, 59),
    high_scores=st.lists(st.integers(98, 100), min_size=4, max_size=6),
)
@example(fx_score=50, high_scores=[100, 100, 100, 100])
def test_any_fx_prevents_scholarship_even_with_high_average(
    fx_score: int, high_scores: list[int]
):
    scores = [fx_score, *high_scores]
    assume(fmean(scores) >= 90)

    assert scholarship(_student(scores)) is Scholarship.NONE

"""Automated black-box cases whose inputs were fixed in lab 3."""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from student_portal.corrections import correct_grade
from student_portal.exceptions import (
    CorrectionPeriodError,
    InvalidGradeError,
    InvalidTransitionError,
)
from student_portal.grades import Grade
from student_portal.people import Funding, Student
from student_portal.scholarship import scholarship
from student_portal.status import Event, Status

SPEC = json.loads(
    (Path(__file__).resolve().parents[3] / "docs/lab03/spec_cases.json").read_text()
)
EXCEPTIONS = {
    "CorrectionPeriodError": CorrectionPeriodError,
    "InvalidGradeError": InvalidGradeError,
}
KNOWN = {
    "ТВ-EP-04": "#12",
    "ТВ-EP-05": "#12",
    "ТВ-EP-06": "#12",
    "ТВ-EP-07": "#12",
    "ТВ-EP-08": "#12",
    "ТВ-EP-09": "#13",
    "ТВ-BVA-04": "#14",
    "ТВ-DT-07": "#15",
    "ТВ-DT-19": "#18 (питання до Р-17)",
    "ТВ-ST-08": "#16",
    "ТВ-ST-16": "#17",
    "ТВ-ST-19": "#16",
}
BASE = date(2026, 10, 1)


def case_param(case):
    issue = KNOWN.get(case["id"])
    marks = (
        pytest.mark.xfail(strict=True, reason=f"відоме розходження {issue}")
        if issue
        else ()
    )
    return pytest.param(case, id=case["id"], marks=marks)


def assert_correction(case):
    original = Grade("Python", 70, BASE)
    today = BASE + timedelta(days=case["d"])
    expected = case["expect"]

    if expected.startswith("Grade:"):
        actual = correct_grade(original, case["score"], today)
        assert actual == Grade("Python", int(expected.split(":")[1]), BASE)
    else:
        with pytest.raises(EXCEPTIONS[expected]):
            correct_grade(original, case["score"], today)
    assert original == Grade("Python", 70, BASE)


@pytest.mark.parametrize("case", [case_param(c) for c in SPEC["corrections"][:11]])
def test_equivalence_classes(case):
    assert_correction(case)


@pytest.mark.parametrize("case", [case_param(c) for c in SPEC["corrections"][11:]])
def test_boundary_values(case):
    assert_correction(case)


@pytest.mark.parametrize("case", [case_param(c) for c in SPEC["scholarship"]])
def test_decision_table(case):
    student = Student(
        1,
        "Олена",
        "Коваль",
        [Grade(f"Курс {i}", score, BASE) for i, score in enumerate(case["scores"])],
        funding=Funding[case["funding"]],
        status=Status[case.get("status", "ACTIVE")],
    )

    actual = scholarship(student)

    assert actual.name == case["expect"]


def test_valid_transition_sequence():
    student = Student(1, "Олена", "Коваль")
    state = SPEC["state"]

    for event, expected in zip(
        state["valid_sequence"], state["valid_expected"], strict=True
    ):
        before = list(student.grades)
        if event == "ADD_GRADE":
            student.add_grade(Grade("Python", 80, BASE))
            assert len(student.grades) == len(before) + 1
        else:
            student.change_status(Event[event])
            assert student.grades == before
        assert student.status is Status[expected]


@pytest.mark.parametrize(
    "case",
    [case_param(c) for c in [SPEC["state"]["guard_false"], *SPEC["state"]["invalid"]]],
)
def test_invalid_transitions(case):
    student = Student(
        1,
        "Олена",
        "Коваль",
        [
            Grade(f"Курс {i}", score, BASE)
            for i, score in enumerate(case.get("scores", []))
        ],
        status=Status[case["status"]],
    )
    before_status, before_grades = student.status, list(student.grades)

    with pytest.raises(InvalidTransitionError):
        if case["event"] == "ADD_GRADE":
            student.add_grade(Grade("Python", 80, BASE))
        else:
            student.change_status(Event[case["event"]])

    assert student.status is before_status
    assert student.grades == before_grades

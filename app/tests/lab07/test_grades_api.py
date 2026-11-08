"""Grade resource boundaries, ECTS classes, and side effects from R-23."""

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from schemas import GRADE_SCHEMA


def assert_grade(body):
    Draft202012Validator(GRADE_SCHEMA, format_checker=FormatChecker()).validate(body)


@pytest.mark.parametrize(
    "score, expected_status, ects",
    [
        (-1, 422, None),
        pytest.param(
            0,
            201,
            "Fx",
            marks=pytest.mark.xfail(
                strict=True,
                raises=AssertionError,
                reason="відомий дефект Р-23 #33: score=0",
            ),
        ),
        (1, 201, "Fx"),
        (59, 201, "Fx"),
        (60, 201, "E"),
        (66, 201, "E"),
        (67, 201, "D"),
        (74, 201, "D"),
        (75, 201, "C"),
        (81, 201, "C"),
        (82, 201, "B"),
        (89, 201, "B"),
        (90, 201, "A"),
        (100, 201, "A"),
        (101, 422, None),
    ],
)
def test_score_and_ects_boundaries(teacher, created, score, expected_status, ects):
    _, student = created
    response = teacher.post(
        "/api/grades",
        json={"student_id": student["id"], "course": "API", "score": score},
    )
    assert response.status_code == expected_status
    if expected_status == 201:
        assert_grade(response.json())
        assert response.json()["ects"] == ects


@pytest.mark.parametrize(
    "field, value",
    [
        ("score", 75.5),
        ("score", None),
        ("score", "missing"),
        ("course", ""),
        ("course", "А" * 101),
        ("course", None),
        ("course", "missing"),
        ("student_id", None),
        ("student_id", "missing"),
    ],
)
def test_invalid_grade_classes_are_422(teacher, created, field, value):
    _, student = created
    body = {"student_id": student["id"], "course": "API", "score": 75}
    if value == "missing":
        del body[field]
    else:
        body[field] = value
    assert teacher.post("/api/grades", json=body).status_code == 422


def test_grade_for_unknown_student_is_404(teacher):
    assert (
        teacher.post(
            "/api/grades", json={"student_id": 999999, "course": "API", "score": 75}
        ).status_code
        == 404
    )


@pytest.mark.parametrize("length", [1, 100])
def test_course_name_valid_boundaries(teacher, created, length):
    _, student = created
    response = teacher.post(
        "/api/grades",
        json={"student_id": student["id"], "course": "А" * length, "score": 75},
    )
    assert response.status_code == 201
    assert len(response.json()["course"]) == length


def test_seed_grades_are_sorted_by_date(admin):
    response = admin.get("/api/students/1/grades")
    assert response.status_code == 200
    assert [grade["graded_on"] for grade in response.json()] == [
        "2026-10-01",
        "2026-10-08",
    ]
    for grade in response.json():
        assert_grade(grade)


def test_two_grades_update_average_and_are_listed_in_date_order(
    admin, teacher, created
):
    location, student = created
    for score in (90, 80):
        response = teacher.post(
            "/api/grades",
            json={
                "student_id": student["id"],
                "course": f"Course {score}",
                "score": score,
            },
        )
        assert response.status_code == 201
        assert_grade(response.json())
    assert admin.get(location).json()["average"] == 85
    listed = admin.get(f"{location}/grades")
    assert listed.status_code == 200
    assert [grade["score"] for grade in listed.json()] == [90, 80]
    assert [grade["graded_on"] for grade in listed.json()] == sorted(
        grade["graded_on"] for grade in listed.json()
    )
    for grade in listed.json():
        assert_grade(grade)

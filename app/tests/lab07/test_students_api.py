"""Student resource tests against the independent R-23 specification."""

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from schemas import STUDENT_SCHEMA


def assert_student(body):
    Draft202012Validator(STUDENT_SCHEMA, format_checker=FormatChecker()).validate(body)


def test_list_and_get_student_match_schema_and_known_average(admin):
    response = admin.get("/api/students")
    assert response.status_code == 200
    assert response.json()
    for student in response.json():
        assert_student(student)
    first = admin.get("/api/students/1")
    assert first.status_code == 200
    assert_student(first.json())
    assert first.json()["average"] == 92.5
    assert first.json()["last_name"] == "Коваль"


def test_group_filter_returns_matching_and_empty_classes(admin):
    matching = admin.get("/api/students", params={"group": "КН-11"})
    unknown = admin.get("/api/students", params={"group": "НЕВІДОМА"})
    assert matching.status_code == unknown.status_code == 200
    assert matching.json() and all(s["group"] == "КН-11" for s in matching.json())
    assert unknown.json() == []


def test_create_round_trip_location_and_null_average(admin, new_student):
    response = admin.post("/api/students", json={**new_student, "ignored": "field"})
    assert response.status_code == 201
    location = response.headers["Location"]
    assert location == f"/api/students/{response.json()['id']}"
    assert_student(response.json())
    assert response.json()["average"] is None
    assert admin.get(location).json() == response.json()


@pytest.mark.parametrize("field", ["first_name", "last_name"])
@pytest.mark.parametrize("length, expected", [(0, 422), (1, 201), (50, 201), (51, 422)])
def test_name_length_boundaries(admin, new_student, field, length, expected):
    response = admin.post("/api/students", json={**new_student, field: "А" * length})
    assert response.status_code == expected
    if expected == 201:
        assert len(response.json()[field]) == length


@pytest.mark.parametrize("field", ["first_name", "last_name", "email"])
@pytest.mark.parametrize("invalid", [None, "missing"])
def test_required_fields_reject_null_and_absence(admin, new_student, field, invalid):
    body = new_student.copy()
    if invalid == "missing":
        del body[field]
    else:
        body[field] = None
    assert admin.post("/api/students", json=body).status_code == 422


def test_invalid_email_is_rejected(admin, new_student):
    assert (
        admin.post(
            "/api/students", json={**new_student, "email": "not-an-email"}
        ).status_code
        == 422
    )


def test_create_rejects_email_duplicate_ignoring_case(admin, new_student):
    assert admin.post("/api/students", json=new_student).status_code == 201
    duplicate = {**new_student, "email": new_student["email"].upper()}
    assert admin.post("/api/students", json=duplicate).status_code == 409


def test_update_round_trip_and_keep_own_email(admin, created):
    location, original = created
    body = {
        "first_name": "Марія",
        "last_name": "Ткачук",
        "email": original["email"],
    }
    response = admin.put(location, json=body)
    assert response.status_code == 200
    assert_student(response.json())
    assert response.json()["first_name"] == "Марія"
    assert admin.get(location).json() == response.json()


@pytest.mark.parametrize(
    "change",
    [
        {"first_name": ""},
        {"last_name": "А" * 51},
        {"email": "invalid"},
        {"email": None},
        {"first_name": "missing"},
    ],
)
def test_update_rejects_invalid_body_without_changing_student(admin, created, change):
    location, original = created
    body = {
        "first_name": original["first_name"],
        "last_name": original["last_name"],
        "email": original["email"],
    }
    for field, value in change.items():
        if value == "missing":
            del body[field]
        else:
            body[field] = value
    assert admin.put(location, json=body).status_code == 422
    assert admin.get(location).json() == original


@pytest.mark.xfail(
    strict=True, raises=AssertionError, reason="відомий дефект Р-23 #31: PUT email"
)
def test_update_rejects_another_students_email_ignoring_case(admin, created):
    location, original = created
    changed = {
        "first_name": original["first_name"],
        "last_name": original["last_name"],
        "email": "O.KOVAL@STUDENTS.EXAMPLE.EDU",
    }
    assert admin.put(location, json=changed).status_code == 409
    assert admin.get(location).json()["email"] == original["email"]


def test_delete_returns_no_body_then_get_is_404(admin, created):
    location, _ = created
    response = admin.delete(location)
    assert response.status_code == 204
    assert response.content == b""
    assert admin.get(location).status_code == 404


@pytest.mark.parametrize(
    "method",
    [
        "GET",
        "PUT",
        pytest.param(
            "DELETE",
            marks=pytest.mark.xfail(
                strict=True,
                raises=AssertionError,
                reason="відомий дефект Р-23 #32: DELETE неіснуючого id",
            ),
        ),
    ],
)
def test_unknown_student_is_404(admin, method, new_student):
    response = admin.request(
        method, "/api/students/999999", json=new_student if method == "PUT" else None
    )
    assert response.status_code == 404


def test_update_rejects_invalid_body(admin, created):
    location, _ = created
    assert admin.put(location, json={"first_name": ""}).status_code == 422

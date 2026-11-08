"""Role-by-operation access matrix, including BOLA and function permissions."""

import pytest
from conftest import client_for

# Each row is an independent R-23 expectation. Writes target a newly created
# student belonging only to that invocation of the parametrized test.
OPERATIONS = {
    "list": ("GET", "/api/students", None),
    "create": ("POST", "/api/students", "student"),
    "get_1": ("GET", "/api/students/1", None),
    "get_2": ("GET", "/api/students/2", None),
    "update": ("PUT", "created", "student"),
    "delete": ("DELETE", "created", None),
    "add_grade": ("POST", "/api/grades", "grade"),
    "grades_1": ("GET", "/api/students/1/grades", None),
    "grades_2": ("GET", "/api/students/2/grades", None),
}

# Columns follow OPERATIONS insertion order.
ROLES = {
    "anonymous": (None, [401] * 9),
    "unknown": ("unknown-token", [401] * 9),
    "admin": ("admin-token", [200, 201, 200, 200, 200, 204, 403, 200, 200]),
    "teacher": ("teacher-token", [200, 403, 200, 200, 403, 403, 201, 200, 200]),
    "student_1": ("student-1-token", [403, 403, 200, 403, 403, 403, 403, 200, 403]),
    "student_2": ("student-2-token", [403, 403, 403, 200, 403, 403, 403, 403, 200]),
}


def _access_case(role, token, operation, expected):
    marks = []
    if role == "teacher" and operation == "update":
        marks.append(
            pytest.mark.xfail(
                strict=True,
                raises=AssertionError,
                reason="відомий дефект Р-23 #34: викладач може PUT",
            )
        )
    if (role, operation) in (
        ("student_1", "grades_2"),
        ("student_2", "grades_1"),
    ):
        marks.append(
            pytest.mark.xfail(
                strict=True,
                raises=AssertionError,
                reason="відомий дефект Р-23 #35: BOLA оцінок",
            )
        )
    return pytest.param(
        role,
        token,
        operation,
        expected,
        marks=marks,
        id=f"{role}-{operation}-{expected}",
    )


MATRIX = [
    _access_case(role, token, operation, expected)
    for role, (token, expected_codes) in ROLES.items()
    for operation, expected in zip(OPERATIONS, expected_codes, strict=True)
]


@pytest.mark.parametrize("role, token, operation, expected", MATRIX)
def test_role_operation_matrix(
    base_url, new_student, created, role, token, operation, expected
):
    method, path, payload = OPERATIONS[operation]
    if path == "created":
        path = created[0]
    body = None
    if payload == "student":
        body = new_student
        if operation == "create":
            body = {**new_student, "email": f"access.{new_student['email']}"}
    elif payload == "grade":
        body = {"student_id": created[1]["id"], "course": "API", "score": 80}

    with client_for(base_url, token) as client:
        response = client.request(method, path, json=body)
    assert response.status_code == expected


@pytest.mark.parametrize(
    "token, path, expected",
    [
        (None, "/api/students/999999", 401),
        ("unknown-token", "/api/students/999999", 401),
        ("student-1-token", "/api/students/999999", 403),
        ("admin-token", "/api/students/999999", 404),
        ("teacher-token", "/api/students/999999", 404),
        pytest.param(
            "student-1-token",
            "/api/students/999999/grades",
            403,
            marks=pytest.mark.xfail(
                strict=True,
                raises=AssertionError,
                reason="відомий дефект Р-23 #35: BOLA розкриває існування",
            ),
        ),
        ("admin-token", "/api/students/999999/grades", 404),
    ],
)
def test_auth_before_permission_before_existence(base_url, token, path, expected):
    with client_for(base_url, token) as client:
        response = client.get(path)
    assert response.status_code == expected


@pytest.mark.parametrize(
    "token, method, path, body",
    [
        ("student-1-token", "POST", "/api/students", {}),
        pytest.param(
            "teacher-token",
            "PUT",
            "created",
            {},
            marks=pytest.mark.xfail(
                strict=True,
                raises=AssertionError,
                reason="відомий дефект Р-23 #34: права PUT",
            ),
        ),
        ("admin-token", "POST", "/api/grades", {}),
    ],
)
def test_permission_check_precedes_body_validation(
    base_url, created, token, method, path, body
):
    if path == "created":
        path = created[0]
    with client_for(base_url, token) as client:
        response = client.request(method, path, json=body)
    assert response.status_code == 403


def test_authentication_precedes_body_validation(anonymous):
    assert anonymous.post("/api/students", json={}).status_code == 401


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект Р-23 #39: голий токен приймається",
)
def test_bare_token_without_bearer_scheme_is_rejected(base_url):
    with client_for(base_url, None) as client:
        response = client.get("/api/students", headers={"Authorization": "admin-token"})
    assert response.status_code == 401

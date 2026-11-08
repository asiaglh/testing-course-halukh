"""Compare actual malformed-JSON responses with the published OpenAPI contract."""

import pytest


@pytest.mark.parametrize("path", ["/api/students", "/api/grades"])
def test_malformed_json_returns_400(admin, teacher, path):
    client = admin if path == "/api/students" else teacher
    response = client.post(
        path, content=b"\xff\x1f", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект OpenAPI #38: код 400 не документовано",
)
@pytest.mark.parametrize("path", ["/api/students", "/api/grades"])
def test_openapi_documents_malformed_json_response(admin, path):
    schema = admin.get("/openapi.json").json()
    assert "400" in schema["paths"][path]["post"]["responses"]

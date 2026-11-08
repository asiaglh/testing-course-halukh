"""R-24 consumer propagates HTTP error responses."""

import httpx
import pytest

from student_portal.dean_client import fetch_student_card


def test_fetch_student_card_raises_for_http_error(monkeypatch):
    def missing(url, headers, timeout):
        return httpx.Response(404, request=httpx.Request("GET", url))

    monkeypatch.setattr("student_portal.dean_client.httpx.get", missing)
    with pytest.raises(httpx.HTTPStatusError):
        fetch_student_card("http://portal", "admin-token", 999999)

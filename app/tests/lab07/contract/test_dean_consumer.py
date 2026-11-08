"""R-24 consumer expectations, captured as a Pact V4 contract."""

import shutil
from pathlib import Path

import pytest
from pact import Pact, match

from student_portal.dean_client import StudentCard, fetch_student_card

PACTS = Path(__file__).parent / "pacts"


@pytest.fixture(scope="module", autouse=True)
def fresh_pacts():
    """Rebuild the contract from every consumer test in this module."""
    shutil.rmtree(PACTS, ignore_errors=True)


@pytest.fixture
def pact():
    contract = Pact("dean-office", "student-portal").with_specification("V4")
    yield contract
    contract.write_file(PACTS)


def _student_body(student_id: int, first: str, last: str, email: str, average):
    return {
        "id": match.int(student_id),
        "first_name": match.str(first),
        "last_name": match.str(last),
        "email": match.str(email),
        "group": match.str("КН-11"),
        "average": average,
        "funding": match.regex(
            "державне замовлення", regex="^(державне замовлення|контракт)$"
        ),
    }


def _interaction(pact, student_id: int, state: str, body):
    (
        pact.upon_receiving(f"картка студента {student_id}")
        .given(state)
        .with_request("GET", f"/api/students/{student_id}")
        .with_header(
            "Authorization", match.regex("Bearer admin-token", regex=r"Bearer .+")
        )
        .will_respond_with(200)
        .with_body(body)
    )


def test_card_of_student_with_grades(pact):
    _interaction(
        pact,
        1,
        "студент з id 1 має оцінки",
        _student_body(
            1, "Олена", "Коваль", "o.koval@students.example.edu", match.number(92.5)
        ),
    )
    with pact.serve() as server:
        card = fetch_student_card(str(server.url), "admin-token", 1)
    assert card == StudentCard(
        "Коваль Олена", "o.koval@students.example.edu", "КН-11", "92.5", True
    )


@pytest.mark.xfail(
    strict=True,
    raises=TypeError,
    reason="відомий дефект Р-24 #36: average=null",
)
def test_card_of_student_without_grades(pact):
    _interaction(
        pact,
        5,
        "студент з id 5 не має оцінок",
        _student_body(
            5, "Софія", "Ткачук", "s.tkachuk@students.example.edu", match.null()
        ),
    )
    with pact.serve() as server:
        card = fetch_student_card(str(server.url), "admin-token", 5)
    assert card == StudentCard(
        "Ткачук Софія", "s.tkachuk@students.example.edu", "КН-11", "-", True
    )

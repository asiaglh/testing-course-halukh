"""Verify the recorded dean-office contract against the real API."""

from pathlib import Path

import pytest
from pact import Verifier

PACTS = Path(__file__).parent / "pacts"


@pytest.mark.xfail(
    strict=True,
    raises=RuntimeError,
    reason="відомий дефект контракту #37: відсутнє funding",
)
def test_student_portal_honours_dean_contract(base_url):
    assert (PACTS / "dean-office-student-portal.json").is_file()
    verifier = (
        Verifier("student-portal", host="127.0.0.1")
        .add_transport(url=base_url)
        .add_source(PACTS)
        .state_handler(
            {
                "студент з id 1 має оцінки": lambda action, parameters: None,
                "студент з id 5 не має оцінок": lambda action, parameters: None,
            }
        )
    )
    verifier.verify()

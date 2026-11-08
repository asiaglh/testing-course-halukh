"""Specification focused examples added after the initial mutation run."""

from datetime import date

import pytest

from student_portal.corrections import correct_grade
from student_portal.exceptions import CorrectionPeriodError
from student_portal.grades import Grade


def test_expired_correction_reports_the_actual_deadline():
    grade = Grade("Python", 70, date(2026, 10, 1))

    with pytest.raises(CorrectionPeriodError) as error:
        correct_grade(grade, 80, today=date(2026, 10, 16))

    assert "15.10.2026" in str(error.value)

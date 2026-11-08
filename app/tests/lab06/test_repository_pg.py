"""Specification checks for R-22 against PostgreSQL."""

from datetime import date

import psycopg
import pytest

from student_portal.exceptions import DuplicateStudentError, StudentNotFoundError
from student_portal.grades import Grade
from student_portal.people import Funding, Student
from student_portal.status import Status


def _student(student_id: int, first: str, last: str) -> Student:
    return Student(student_id, first, last)


def test_schema_creation_is_idempotent(repository):
    repository.create_schema()
    repository.create_schema()
    repository.add(_student(1, "Анна", "Галух"))
    assert repository.get(1).last_name == "Галух"


def test_add_get_round_trip_all_fields(repository):
    student = Student(
        1,
        "Анна",
        "Галух",
        [Grade("Математика", 95, date(2026, 10, 1))],
        "anna@example.edu",
        funding=Funding.CONTRACT,
        status=Status.ON_LEAVE,
    )
    repository.add(student)
    assert repository.get(1) == student


@pytest.mark.xfail(
    strict=True,
    raises=psycopg.errors.UniqueViolation,
    reason="відомий дефект Р-22 #26: повторний id",
)
def test_duplicate_id_has_domain_error_and_leaves_connection_usable(repository):
    original = _student(1, "Анна", "Галух")
    repository.add(original)

    with pytest.raises(DuplicateStudentError):
        repository.add(_student(1, "Ірина", "Коваль"))

    assert repository.get(1) == original
    repository.add(_student(2, "Олена", "Мельник"))
    assert repository.get(2).last_name == "Мельник"


def test_get_returns_grades_ordered_by_date(repository):
    repository.add(
        Student(
            1,
            "Анна",
            "Галух",
            [
                Grade("Пізня", 80, date(2026, 10, 9)),
                Grade("Рання", 90, date(2026, 10, 1)),
            ],
        )
    )
    assert [g.course for g in repository.get(1).grades] == ["Рання", "Пізня"]


def test_get_unknown_student_raises_domain_error(repository):
    with pytest.raises(StudentNotFoundError):
        repository.get(999)


def test_add_grade_to_existing_student(repository):
    repository.add(_student(1, "Анна", "Галух"))
    grade = Grade("Тестування", 93, date(2026, 10, 3))
    repository.add_grade(1, grade)
    assert repository.get(1).grades == [grade]


def test_add_grade_to_unknown_student_leaves_connection_usable(repository):
    with pytest.raises(StudentNotFoundError):
        repository.add_grade(999, Grade("Тестування", 93))
    repository.add(_student(1, "Анна", "Галух"))
    assert repository.get(1).first_name == "Анна"


def test_find_trims_whitespace_and_empty_query_returns_everyone(repository):
    repository.add(_student(1, "Анна", "Галух"))
    repository.add(_student(2, "Ірина", "Коваль"))
    assert [s.id for s in repository.find("  алух  ")] == [1]
    assert [s.id for s in repository.find("")] == [1, 2]


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект Р-22 #27: регістр кирилиці",
)
def test_find_ignores_case_of_cyrillic(repository):
    repository.add(_student(1, "Анна", "Галух"))
    assert [s.id for s in repository.find("ГАЛУХ")] == [1]


@pytest.mark.parametrize("symbol", ["%", "_"])
@pytest.mark.xfail(
    strict=True, raises=AssertionError, reason="відомий дефект Р-22 #28: шаблони LIKE"
)
def test_find_treats_sql_wildcards_as_literal_characters(repository, symbol):
    repository.add(_student(1, "Анна", f"А{symbol}Б"))
    repository.add(_student(2, "Ірина", "АВБ"))
    assert [s.id for s in repository.find(symbol)] == [1]


def test_find_sorts_same_last_name_by_first_name(repository):
    repository.add(_student(1, "Яна", "Галух"))
    repository.add(_student(2, "Анна", "Галух"))
    assert [s.id for s in repository.find("Галух")] == [2, 1]


@pytest.mark.xfail(
    strict=True, raises=AssertionError, reason="відомий дефект Р-22 #29: колація"
)
def test_find_uses_ukrainian_alphabet_order(repository):
    for student_id, last in enumerate(["Їжак", "Євген", "Іван", "Ґудзик"], 1):
        repository.add(_student(student_id, "Анна", last))
    assert [s.last_name for s in repository.find("")] == [
        "Ґудзик",
        "Євген",
        "Іван",
        "Їжак",
    ]

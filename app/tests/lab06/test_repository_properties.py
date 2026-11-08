"""Round-trip property with a fresh rollback for every generated example."""

from datetime import date

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from student_portal.grades import Grade
from student_portal.people import Funding, Student
from student_portal.status import Status

grades = st.lists(
    st.builds(
        Grade,
        course=st.sampled_from(["Математика", "Історія", "Python"]),
        score=st.integers(0, 100),
        graded_on=st.dates(min_value=date(2025, 1, 1), max_value=date(2026, 12, 31)),
    ),
    max_size=5,
).map(lambda values: sorted(values, key=lambda grade: grade.graded_on))

students = st.builds(
    Student,
    id=st.just(1),
    first_name=st.sampled_from(["Анна", "Ірина", "Олена", "Єва"]),
    last_name=st.sampled_from(["Галух", "Коваль", "Ґудзик", "Їжак"]),
    grades=grades,
    email=st.one_of(st.none(), st.just("student@example.edu")),
    funding=st.sampled_from(list(Funding)),
    status=st.sampled_from(list(Status)),
)


@settings(
    max_examples=60,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(student=students)
def test_student_survives_postgres_round_trip(repository, student):
    with repository.connection.transaction(force_rollback=True):
        repository.add(student)
        assert repository.get(student.id) == student

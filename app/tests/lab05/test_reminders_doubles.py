"""R-20 contract tests: every message stays inside a test double."""

from datetime import date
from unittest.mock import create_autospec

import pytest

from student_portal import reminders
from student_portal.grades import Grade
from student_portal.group import Group
from student_portal.people import Student
from student_portal.reminders import (
    SUBJECT,
    Mailer,
    ReminderReport,
    SmtpMailer,
    send_debt_reminders,
)
from student_portal.status import Status

TODAY = date(2026, 11, 2)
TEST_CREDENTIAL = "test-value"


class FakeMailer:
    def __init__(self):
        self.outbox = []

    def send(self, to, subject, body):
        self.outbox.append((to, subject, body))


def student(student_id, scores=(45,), *, status=Status.ACTIVE, email=None):
    return Student(
        student_id,
        "Олена",
        "Коваль",
        [Grade(f"Course {i}", score) for i, score in enumerate(scores)],
        email=email,
        status=status,
    )


def group_with(*students):
    group = Group("КН-11")
    for item in students:
        group.add(item)
    return group


def test_fake_single_course_happy_path():
    group = group_with(student(1, email="o@example.edu"))
    mailer = FakeMailer()

    report = send_debt_reminders(group, mailer, today=TODAY)

    assert report == ReminderReport(sent=["o@example.edu"], failed=[])
    assert len(mailer.outbox) == 1
    to, subject, body = mailer.outbox[0]
    assert (to, subject) == ("o@example.edu", SUBJECT)
    assert "Course 0" in body
    assert "02.12.2026" in body


@pytest.mark.xfail(strict=True, reason="відомий дефект #22")
def test_fake_one_letter_lists_all_fx_courses_in_order():
    debtor = Student(
        1,
        "Олена",
        "Коваль",
        [Grade("Zoology", 40), Grade("Algebra", 50), Grade("Algebra", 55)],
        email="o@example.edu",
    )
    group = group_with(debtor)
    mailer = FakeMailer()

    report = send_debt_reminders(group, mailer, today=TODAY)

    assert report.sent == ["o@example.edu"]
    assert report.failed == []
    assert len(mailer.outbox) == 1
    to, subject, body = mailer.outbox[0]
    assert (to, subject) == ("o@example.edu", SUBJECT)
    assert "Algebra, Zoology" in body
    assert "02.12.2026" in body


def test_autospec_eligible_student_receives_one_message():
    group = group_with(student(1, email="o@example.edu"))
    mailer = create_autospec(Mailer, instance=True)

    report = send_debt_reminders(group, mailer, today=TODAY)

    mailer.send.assert_called_once()
    args = mailer.send.call_args.args
    assert args[0:2] == ("o@example.edu", SUBJECT)
    assert "Course 0" in args[2]
    assert report == ReminderReport(sent=["o@example.edu"], failed=[])


@pytest.mark.parametrize(
    ("status", "email", "scores"),
    [
        pytest.param(
            Status.ON_LEAVE,
            "o@example.edu",
            (45,),
            id="on-leave",
            marks=pytest.mark.xfail(strict=True, reason="відомий дефект #21"),
        ),
        pytest.param(Status.EXPELLED, "o@example.edu", (45,), id="expelled"),
        pytest.param(
            Status.GRADUATED,
            "o@example.edu",
            (45,),
            id="graduated",
            marks=pytest.mark.xfail(strict=True, reason="відомий дефект #21"),
        ),
        pytest.param(Status.ACTIVE, None, (45,), id="missing-email"),
        pytest.param(Status.ACTIVE, "o@example.edu", (60,), id="no-fx"),
    ],
)
def test_autospec_ineligible_student_is_not_contacted(status, email, scores):
    group = group_with(student(1, scores, status=status, email=email))
    mailer = create_autospec(Mailer, instance=True)

    report = send_debt_reminders(group, mailer, today=TODAY)

    mailer.send.assert_not_called()
    assert report == ReminderReport(sent=[], failed=[])


@pytest.mark.xfail(strict=True, reason="відомий дефект #23")
def test_autospec_first_failure_does_not_stop_second_student():
    group = group_with(
        student(1, email="first@example.edu"),
        student(2, email="second@example.edu"),
    )
    mailer = create_autospec(Mailer, instance=True)
    mailer.send.side_effect = [ConnectionError("SMTP unavailable"), None]

    report = send_debt_reminders(group, mailer, today=TODAY)

    assert mailer.send.call_count == 2
    assert report == ReminderReport(
        sent=["second@example.edu"], failed=["first@example.edu"]
    )


def test_patching_smtplib_does_not_replace_imported_name(mocker):
    original = reminders.SMTP

    wrong_patch = mocker.patch("smtplib.SMTP")

    assert reminders.SMTP is original
    assert reminders.SMTP is not wrong_patch


def test_smtp_uses_default_port_without_login(mocker):
    smtp_class = mocker.patch("student_portal.reminders.SMTP")
    smtp = smtp_class.return_value.__enter__.return_value

    SmtpMailer("smtp.example.edu").send("o@example.edu", SUBJECT, "body")

    smtp_class.assert_called_once_with("smtp.example.edu", 587, timeout=10)
    smtp.starttls.assert_called_once_with()
    smtp.login.assert_not_called()
    smtp.send_message.assert_called_once()


@pytest.mark.parametrize("username", [None, "operator"])
def test_smtp_mailer_uses_tls_and_expected_headers(mocker, username):
    smtp_class = mocker.patch("student_portal.reminders.SMTP")
    smtp = smtp_class.return_value.__enter__.return_value
    mailer = SmtpMailer(
        "smtp.example.edu", port=2525, username=username, password=TEST_CREDENTIAL
    )

    mailer.send("o@example.edu", SUBJECT, "Перескладання до 02.12.2026")

    smtp_class.assert_called_once_with("smtp.example.edu", 2525, timeout=10)
    smtp.starttls.assert_called_once_with()
    if username:
        smtp.login.assert_called_once_with("operator", TEST_CREDENTIAL)
    else:
        smtp.login.assert_not_called()
    smtp.send_message.assert_called_once()
    message = smtp.send_message.call_args.args[0]
    assert message["From"] == "dekanat@vnu.example.edu"
    assert message["To"] == "o@example.edu"
    assert message["Subject"] == SUBJECT
    assert "Перескладання до 02.12.2026" in message.get_content()

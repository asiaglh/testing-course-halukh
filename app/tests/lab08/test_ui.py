"""E2E-правила Р-25 з незалежними очікуваннями для кожної ролі."""

import re

import pytest
from playwright.sync_api import expect

from .pages.login_page import LoginPage
from .pages.student_card import StudentCard
from .pages.students_page import StudentsPage


def test_unknown_token_keeps_login_and_shows_alert(page, base_url):
    login = LoginPage(page, base_url).open()
    login.login("wrong-token")
    expect(login.error).to_have_text("Невідомий токен")
    expect(login.form).to_be_visible()
    expect(login.logout_button).to_be_hidden()


@pytest.mark.parametrize(
    ("token", "role"),
    [("admin-token", "Адміністратор"), ("teacher-token", "Викладач")],
)
def test_staff_login_role_and_logout(page, base_url, token, role):
    login = LoginPage(page, base_url).open()
    login.login(token)
    students = StudentsPage(page).wait_loaded()
    expect(login.role).to_have_text(role)
    expect(login.logout_button).to_be_visible()
    expect(students.heading).to_be_visible()
    login.logout()
    expect(login.form).to_be_visible()
    expect(students.heading).to_be_hidden()
    expect(login.logout_button).to_be_hidden()


@pytest.mark.parametrize(
    ("token", "name"),
    [("student-1-token", "Коваль Олена"), ("student-2-token", "Мельник Андрій")],
)
def test_student_sees_only_own_card_without_staff_controls(page, base_url, token, name):
    login = LoginPage(page, base_url).open()
    login.login(token)
    card = StudentCard(page)
    expect(login.role).to_have_text("Студент")
    expect(card.name).to_have_text(name)
    expect(card.back_button).to_be_hidden()
    expect(card.grade_form).to_be_hidden()
    expect(StudentsPage(page).heading).to_be_hidden()
    login.logout()
    expect(login.form).to_be_visible()


def test_admin_list_columns_values_and_actions(as_admin):
    students = as_admin
    for column in ("ПІБ", "Email", "Середній бал"):
        expect(students.page.get_by_role("columnheader", name=column)).to_be_visible()
    expect(students.row_for("Коваль Олена")).to_contain_text(
        "o.koval@students.example.edu"
    )
    expect(students.row_for("Ткачук Софія")).to_be_visible()
    expect(students.average_of("Ткачук Софія")).to_have_text("-")
    expect(students.total).to_have_text(re.compile(r"Усього: \d+"))
    expect(students.add_form).to_be_visible()
    expect(
        students.row_for("Коваль Олена").get_by_role("button", name="Видалити")
    ).to_be_visible()


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект #41: формат середнього бала",
)
@pytest.mark.parametrize(
    ("name", "average"), [("Коваль Олена", "92,5"), ("Шевчук Ірина", "82,0")]
)
def test_list_average_has_one_decimal(as_admin, name, average):
    expect(as_admin.average_of(name)).to_have_text(average, timeout=1500)


def test_teacher_can_view_cards_but_not_admin_actions(as_teacher):
    students = as_teacher
    expect(students.add_form).to_be_hidden()
    expect(students.page.get_by_role("button", name="Видалити")).to_have_count(0)
    students.open_card("Коваль Олена")
    card = StudentCard(students.page)
    expect(card.name).to_have_text("Коваль Олена")
    expect(card.grade_form).to_be_visible()
    expect(card.back_button).to_be_visible()


def test_search_by_partial_surname_and_empty_result(as_admin):
    students = as_admin
    students.search_for("Ков")
    expect(students.rows).to_have_count(1)
    expect(students.row_for("Коваль Олена")).to_be_visible()
    students.search_for("немає-такого-прізвища")
    expect(students.rows).to_have_count(0)
    expect(students.empty).to_be_visible()


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект #42: пошук чутливий до регістру",
)
def test_search_ignores_case(as_admin):
    students = as_admin
    students.search_for("кОВ")
    expect(students.row_for("Коваль Олена")).to_be_visible(timeout=1500)
    expect(students.rows).to_have_count(1)


def test_add_success_updates_row_total_message_and_clears_form(as_admin, unique_email):
    students = as_admin
    before = students.rows.count()
    students.add_student("Пробний", "Марко", unique_email)
    expect(students.message).to_have_text("Студента додано: Пробний Марко")
    expect(students.row_for("Пробний Марко")).to_be_visible()
    expect(students.rows).to_have_count(before + 1)
    expect(students.total).to_have_text(f"Усього: {before + 1}")
    expect(students.last_name).to_be_empty()
    expect(students.first_name).to_be_empty()
    expect(students.email).to_be_empty()


def test_duplicate_email_shows_error_and_keeps_table(as_admin):
    students = as_admin
    before = students.rows.count()
    students.add_student("Дубль", "Марко", "O.KOVAL@STUDENTS.EXAMPLE.EDU")
    expect(students.error).to_have_text("Помилка: email уже використовується")
    expect(students.rows).to_have_count(before)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект #43: поля форми очищуються після 409",
)
def test_duplicate_email_keeps_input_for_correction(as_admin):
    students = as_admin
    students.add_student("Дубль", "Марко", "O.KOVAL@STUDENTS.EXAMPLE.EDU")
    expect(students.error).to_have_text("Помилка: email уже використовується")
    expect(students.last_name).to_have_value("Дубль", timeout=1500)
    expect(students.first_name).to_have_value("Марко")
    expect(students.email).to_have_value("O.KOVAL@STUDENTS.EXAMPLE.EDU")


def test_invalid_student_data_shows_error_and_keeps_table(as_admin, unique_email):
    students = as_admin
    before = students.rows.count()
    students.add_student("Д" * 51, "Марко", unique_email)
    expect(students.error).to_have_text("Помилка: перевірте поля форми")
    expect(students.rows).to_have_count(before)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект #43: поля форми очищуються після 422",
)
def test_invalid_student_data_keeps_input_for_correction(as_admin, unique_email):
    students = as_admin
    students.add_student("Д" * 51, "Марко", unique_email)
    expect(students.error).to_have_text("Помилка: перевірте поля форми")
    expect(students.last_name).to_have_value("Д" * 51, timeout=1500)
    expect(students.email).to_have_value(unique_email)


def _add_for_deletion(students: StudentsPage, email: str) -> tuple[str, int]:
    before = students.rows.count()
    students.add_student("Тимчасова", "Олена", email)
    expect(students.message).to_have_text("Студента додано: Тимчасова Олена")
    expect(students.row_for("Тимчасова Олена")).to_be_visible()
    return "Тимчасова Олена", before


def test_delete_confirm_removes_row_and_shows_message(as_admin, unique_email):
    students = as_admin
    name, _ = _add_for_deletion(students, unique_email)
    dialogs = []
    students.delete(name, accept=True, dialogs=dialogs)
    assert dialogs == [f"Видалити студента {name}?"]
    expect(students.message).to_have_text("Студента видалено")
    expect(students.row_for(name)).to_have_count(0)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект #45: лічильник не зменшується",
)
def test_delete_confirm_decrements_total(as_admin, unique_email):
    students = as_admin
    name, before = _add_for_deletion(students, unique_email)
    students.delete(name, accept=True, dialogs=[])
    expect(students.message).to_have_text("Студента видалено")
    expect(students.total).to_have_text(f"Усього: {before}", timeout=1500)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект #44: скасування видаляє студента",
)
def test_delete_cancel_sends_no_delete_request(as_admin, unique_email):
    students = as_admin
    name, before = _add_for_deletion(students, unique_email)
    sent = []
    students.page.on(
        "request",
        lambda request: (
            sent.append(request.url)
            if request.method == "DELETE" and "/api/students/" in request.url
            else None
        ),
    )
    dialogs = []
    students.delete(name, accept=False, dialogs=dialogs)
    assert dialogs == [f"Видалити студента {name}?"]
    students.page.wait_for_timeout(100)
    assert sent == []
    expect(students.row_for(name)).to_be_visible()
    expect(students.total).to_have_text(f"Усього: {before + 1}")


def test_card_shows_grades_average_and_returns_to_list(as_admin):
    students = as_admin
    students.open_card("Коваль Олена")
    card = StudentCard(students.page)
    expect(card.name).to_have_text("Коваль Олена")
    expect(card.average).to_have_text("92,5")
    for column in ("Дисципліна", "Бали", "ECTS", "Дата"):
        expect(students.page.get_by_role("columnheader", name=column)).to_be_visible()
    expect(card.grade_for("Python")).to_contain_text("95")
    expect(card.grade_for("Python")).to_contain_text("A")
    expect(card.grade_for("Python")).to_contain_text("2026-10-01")
    expect(card.grade_for("Бази даних")).to_contain_text("2026-10-08")
    expect(card.grade_form).to_be_hidden()
    card.back_to_list()
    students.wait_loaded()
    expect(students.row_for("Коваль Олена")).to_be_visible()


def test_teacher_adds_grade_to_own_test_student(created_student, as_teacher):
    students = as_teacher
    students.open_card(created_student["email"])
    card = StudentCard(students.page)
    expect(card.average).to_have_text("-")
    card.add_grade("Тестування", 82)
    expect(card.message).to_have_text("Оцінку виставлено")
    expect(card.average).to_have_text("82,0")
    expect(card.grade_for("Тестування")).to_contain_text("82")
    expect(card.grade_for("Тестування")).to_contain_text("B")
    expect(card.grade_for("Тестування")).to_contain_text(
        re.compile(r"\d{4}-\d{2}-\d{2}")
    )
    expect(card.course).to_be_empty()
    expect(card.score).to_be_empty()


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект #46: список після оцінки не оновлюється",
)
def test_back_to_list_shows_current_average(created_student, as_teacher):
    students = as_teacher
    students.open_card(created_student["email"])
    card = StudentCard(students.page)
    card.add_grade("Тестування", 82)
    expect(card.message).to_have_text("Оцінку виставлено")
    card.back_to_list()
    students.wait_loaded()
    expect(students.average_of(created_student["email"])).to_have_text(
        "82,0", timeout=1500
    )


@pytest.mark.parametrize("score", [-1, 101])
def test_grade_outside_range_shows_error(created_student, as_teacher, score):
    students = as_teacher
    students.open_card(created_student["email"])
    card = StudentCard(students.page)
    card.add_grade("Тестування", score)
    expect(card.error).to_have_text("Помилка: бали від 0 до 100")
    expect(card.grade_for("Тестування")).to_have_count(0)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="відомий дефект Р-23 #33: 0 балів відхиляється API",
)
def test_zero_grade_is_valid(created_student, as_teacher):
    students = as_teacher
    students.open_card(created_student["email"])
    card = StudentCard(students.page)
    card.add_grade("Нульова оцінка", 0)
    expect(card.message).to_have_text("Оцінку виставлено", timeout=1500)
    expect(card.grade_for("Нульова оцінка")).to_contain_text("Fx")

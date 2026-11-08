"""Дії та локатори списку студентів."""

import re

from playwright.sync_api import Locator, Page, expect


class StudentsPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role("heading", name="Студенти групи")
        self.rows = page.locator("#students tr")
        self.search = page.get_by_label("Пошук за прізвищем", exact=True)
        self.total = page.locator("#total")
        self.empty = page.get_by_text("Нікого не знайдено")
        self.add_form = page.locator("#add-form")
        self.last_name = page.get_by_label("Прізвище", exact=True)
        self.first_name = page.get_by_label("Ім’я", exact=True)
        self.email = page.get_by_label("Email", exact=True)
        self.add_button = page.get_by_role("button", name="Додати студента")
        self.message = page.get_by_role("status")
        self.error = page.get_by_role("alert")

    def wait_loaded(self) -> "StudentsPage":
        expect(self.heading).to_be_visible()
        expect(self.total).to_have_text(re.compile(r"Усього: \d+"))
        return self

    def row_for(self, name: str) -> Locator:
        return self.rows.filter(has_text=name)

    def average_of(self, name: str) -> Locator:
        return self.row_for(name).locator("td").nth(2)

    def search_for(self, text: str) -> None:
        self.search.fill(text)

    def add_student(self, last_name: str, first_name: str, email: str) -> None:
        self.last_name.fill(last_name)
        self.first_name.fill(first_name)
        self.email.fill(email)
        self.add_button.click()

    def delete(self, name: str, *, accept: bool, dialogs: list[str]) -> None:
        def respond(dialog):
            dialogs.append(dialog.message)
            if accept:
                dialog.accept()
            else:
                dialog.dismiss()

        self.page.once("dialog", respond)
        self.row_for(name).get_by_role("button", name="Видалити").click()

    def open_card(self, row_text: str) -> None:
        self.row_for(row_text).get_by_role("link").click()

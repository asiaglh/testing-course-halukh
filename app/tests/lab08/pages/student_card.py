"""Дії та локатори картки студента."""

from playwright.sync_api import Locator, Page


class StudentCard:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.name = page.locator("#card-name")
        self.average = page.locator("#card-average")
        self.rows = page.locator("#grades tr")
        self.grade_form = page.locator("#grade-form")
        self.course = page.get_by_label("Дисципліна", exact=True)
        self.score = page.get_by_label("Бали", exact=True)
        self.submit = page.get_by_role("button", name="Виставити")
        self.back_button = page.get_by_role("button", name="До списку")
        self.message = page.get_by_role("status")
        self.error = page.get_by_role("alert")

    def grade_for(self, course: str) -> Locator:
        return self.rows.filter(has_text=course)

    def add_grade(self, course: str, score: int) -> None:
        self.course.fill(course)
        self.score.fill(str(score))
        self.submit.click()

    def back_to_list(self) -> None:
        self.back_button.click()

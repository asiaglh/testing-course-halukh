"""Дії на формі входу та виходу."""

from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url
        self.form = page.locator("#login-form")
        self.token = page.get_by_label("Токен", exact=True)
        self.submit = page.get_by_role("button", name="Увійти")
        self.error = page.get_by_role("alert")
        self.role = page.locator("#role")
        self.logout_button = page.get_by_role("button", name="Вийти")

    def open(self) -> "LoginPage":
        self.page.goto(self.base_url)
        return self

    def login(self, token: str) -> None:
        self.token.fill(token)
        self.submit.click()

    def logout(self) -> None:
        self.logout_button.click()

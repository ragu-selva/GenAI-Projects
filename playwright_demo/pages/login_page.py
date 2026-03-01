from playwright.sync_api import Page, expect

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        # Define all our "Ingredients" (Locators) here in one place
        self.username_input = page.locator("[data-test='username']")
        self.password_input = page.locator("[data-test='password']")
        self.login_button = page.locator("[data-test='login-button']")

    def navigate(self):
        self.page.goto("https://www.saucedemo.com/")

    def login(self, user, pwd):
        # Define the "Recipe" (Action)
        self.username_input.fill(user)
        self.password_input.fill(pwd)
        self.login_button.click()
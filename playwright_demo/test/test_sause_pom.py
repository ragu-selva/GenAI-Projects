import pytest
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect

# 1. Define our data sets: (username, expected_url_part)
@pytest.mark.parametrize("user, url_part", [
    ("standard_user", "inventory"),
    ("problem_user", "inventory"),
    ("performance_glitch_user", "inventory1")
])
def test_multiple_users_login(login_page, user, url_part):
   
    # 3. Execution
    login_page.navigate()
    login_page.login(user, "secret_sauce")

    # 4. Smart Assertion
    # We check if the URL contains the expected word
    expect(login_page.page).to_have_url(f"https://www.saucedemo.com/{url_part}.html")
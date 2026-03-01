import pytest
from pages.login_page import LoginPage

# We define a 'fixture' named login_page
@pytest.fixture
def login_page(page):
    # This happens BEFORE the test
    lp = LoginPage(page)
    return lp
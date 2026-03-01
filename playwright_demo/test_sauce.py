import pytest
from playwright.sync_api import Page, expect

def test_add_to_cart(page: Page):
    # 1. Open the website
    page.goto("https://www.saucedemo.com/")

    # 2. Login - using 'fill' for speed
    page.locator("[data-test='username']").fill("standard_user")
    page.locator("[data-test='password']").fill("secret_sauce")
    page.locator("[data-test='login-button']").click()

    # 3. Assert we are logged in by checking the URL
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")

    # 4. Add the first item (Backpack) to the cart
    # We use a 'data-test' attribute because it's the most stable way to locate elements
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()

    # 5. Verify the shopping cart badge says '1'
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_text("1")
    
    print("Test Passed Successfully!")
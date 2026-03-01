# 🎭 Playwright Python Automation Framework

A professional-grade end-to-end (E2E) testing framework built with **Python**, **Playwright**, and **Pytest**. This project demonstrates advanced automation concepts including the Page Object Model (POM), Data-Driven Testing, and Automated Reporting.

## 🌟 Key Features
- **Page Object Model (POM):** Decoupled UI locators from test logic for high maintainability.
- **Data-Driven Testing:** Uses `@pytest.mark.parametrize` to run tests against multiple user personas.
- **Global Fixtures:** Centralized setup/teardown logic using `conftest.py`.
- **Visual Reporting:** Automated HTML reports with `pytest-html`.
- **Auto-Wait Logic:** Eliminates flaky tests by leveraging Playwright's native waiting mechanisms.
- **Trace Viewer & Debugging:** Integrated support for Playwright Inspector and Trace logs.

## 🏗️ Project Structure
```text
playwright_project/
├── pages/               # Page Object Classes (The "Map")
│   ├── __init__.py
│   └── login_page.py
├── tests/               # Test Scripts (The "Logic")
│   ├── __init__.py
│   ├── conftest.py      # Global Fixtures (The "Factory")
│   └── test_sauce_pom.py
├── requirements.txt     # Dependency snapshot
└── report.html          # Generated test results

🚀 Getting Started
1. Prerequisites
Python 3.8+

Virtual Environment (recommended)

2. Installation
Clone the repository and install the dependencies:

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install libraries
pip install -r requirements.txt

# Install Playwright browsers
playwright install

3. Running Tests
Run all tests (Headless):
python -m pytest

Run in Headed mode with Slow Motion (Watch the robot):
python -m pytest --headed --slowmo 1000

Generate HTML Report:
python -m pytest --html=report.html --self-contained-html

Debug Mode (Step-by-Step):

Windows (PS): $env:PWDEBUG=1; pytest -s

Mac/Linux: PWDEBUG=1 pytest -s

📊 Sample Report
(Attach a screenshot of your report.html here to impress viewers!)

🛠️ Tech Stack
Language: Python

Test Runner: Pytest

Automation: Playwright

Reporting: Pytest-HTML
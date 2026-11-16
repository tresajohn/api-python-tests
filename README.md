# Restful Booker API Test Suite

Standalone Python API test suite for the [Restful Booker](https://restful-booker.herokuapp.com) API.

## Stack

- Python 3.12 · pytest 8 · requests · allure-pytest

## Run locally

```bash
pip install -e .
pytest tests/ -v
```

## Generate Allure report

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

## CI / Live report

GitHub Actions runs all tests on every push to `main` and publishes the interactive Allure report to GitHub Pages.

[View live report](https://tresajohn.github.io/api-python-tests/)

## Coverage

| Area | Scenarios |
|------|-----------|
| Health | Ping endpoint returns 201 |
| Auth | Valid credentials return token · Invalid credentials raise error |
| Bookings (read) | Get all bookings · Get booking by ID |
| Bookings (write) | Create · Full update · Partial update · Delete |
| Edge cases | 404 on missing booking · 403 without auth token |

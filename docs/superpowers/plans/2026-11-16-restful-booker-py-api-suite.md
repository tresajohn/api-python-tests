# Restful Booker Python API Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Python API test suite for Restful Booker with Allure reporting deployed to GitHub Pages via CI.

**Architecture:** Two thin API client classes (`AuthClient`, `BookingClient`) wrap requests calls; pytest fixtures in `conftest.py` wire them together; test files consume only fixtures, never clients directly. Allure decorators on every test provide the report layer.

**Tech Stack:** Python 3.12, pytest 8, requests, allure-pytest, allure-commandline (GitHub Actions CI), GitHub Pages

**Spec:** Conversation design — Restful Booker (https://restful-booker.herokuapp.com), new GitHub repo `restful-booker-py`, clear README, Allure report on GitHub Pages.

## Global Constraints

- Python >= 3.12
- pytest >= 8.0.0
- requests >= 2.32.0
- allure-pytest >= 2.13.5
- Base URL: `https://restful-booker.herokuapp.com` (never hardcoded in tests — from fixture only)
- Auth credentials: username `admin`, password `password123` (public test creds for this API)
- No `.env` file required — credentials are public and built into fixtures
- No `requirements.txt` — deps in `pyproject.toml` only
- Allure results dir: `allure-results/` (set via `pytest.ini` addopts)
- GitHub repo name: `restful-booker-py`

## Review Focus

1. **Shared public API interference** — Restful Booker is public; other users' concurrent runs can delete bookings under test. `created_booking` fixture must create its own booking and clean up by ID, never rely on a pre-existing ID. Covered in Task 4 conftest fixture.
2. **Auth response body, not status code** — `/auth` returns HTTP 200 for both valid and invalid credentials; success has `{"token": "..."}`, failure has `{"reason": "Bad credentials"}`. `create_token` must inspect the body. Covered in Task 2 `test_create_token_invalid_credentials`.
3. **DELETE returns 201** — Restful Booker returns `201 Created` on successful delete, not 200/204. `delete()` must assert status 201 and callers must not assume 200. Covered in Task 4 `test_delete_booking`.
4. **Heroku cold-start timeouts** — First request after idle can hang 10–30s. `requests` default timeout is None (hang forever). All client methods must pass `timeout=10`. Covered as a code constraint in Task 2 (AuthClient) and Task 3 (BookingClient).
5. **403 on auth-required ops without token** — PUT/PATCH/DELETE without a valid token return 403. Client methods must raise `requests.HTTPError` so callers get a clear signal. Covered in Task 4 `test_update_without_token` and `test_delete_without_token`.

---

### Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `pytest.ini`
- Create: `api/__init__.py` (empty)
- Create: `tests/__init__.py` (empty)
- Create: `.gitignore`
- Create: `README.md`
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: nothing
- Produces: runnable `pytest tests/` (zero tests, zero failures); repo pushed to `github.com/tresajohn/restful-booker-py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "restful-booker-py"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.32.0",
    "pytest>=8.0.0",
    "allure-pytest>=2.13.5",
]

[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
```

- [ ] **Step 2: Create `pytest.ini`**

```ini
[pytest]
addopts = --alluredir=allure-results
markers =
    health: health check tests
    auth: authentication tests
    booking: booking CRUD tests
```

- [ ] **Step 3: Create `api/__init__.py` and `tests/__init__.py`** (both empty)

- [ ] **Step 4: Create `.gitignore`**

Include: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `allure-results/`, `allure-report/`, `*.egg-info/`, `.env`

- [ ] **Step 5: Create `README.md`**

```markdown
# Restful Booker API Test Suite

Standalone Python API test suite for the [Restful Booker](https://restful-booker.herokuapp.com) API.

## Stack
- Python 3.12 · pytest 8 · requests · allure-pytest

## Run locally
\`\`\`bash
pip install -e .
pytest tests/ -v
\`\`\`

## Generate Allure report
\`\`\`bash
allure generate allure-results --clean -o allure-report
allure open allure-report
\`\`\`

## CI / Live report
GitHub Actions runs all tests on push to `main` and publishes the Allure report to GitHub Pages.

[View live report](https://tresajohn.github.io/restful-booker-py/)

## Coverage
| Area | Scenarios |
|------|-----------|
| Health | Ping endpoint |
| Auth | Valid token, invalid credentials |
| Bookings | Get all, get by ID, create, full update, partial update, delete |
| Edge cases | 404 on missing booking, 403 without auth token |
```

- [ ] **Step 6: Create `.github/workflows/ci.yml`**

```yaml
name: API Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: pages
  cancel-in-progress: true

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -e .

      - name: Install Allure CLI
        run: |
          curl -sLo allure.tgz https://github.com/allure-framework/allure2/releases/download/2.29.0/allure-2.29.0.tgz
          tar -xzf allure.tgz
          echo "$PWD/allure-2.29.0/bin" >> $GITHUB_PATH

      - name: Run tests
        run: pytest tests/ -v || true

      - name: Generate Allure report
        if: always()
        run: allure generate allure-results --clean -o allure-report

      - name: Upload Allure artifact
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: allure-report
          path: allure-report/
          retention-days: 14

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        if: github.ref == 'refs/heads/main' && always()
        with:
          path: allure-report/

      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
        if: github.ref == 'refs/heads/main' && always()
```

- [ ] **Step 7: Verify scaffold runs with zero tests**

Run: `pip install -e . && pytest tests/ -v`
Expected: `no tests ran` exit 5 (or 0 if pytest.ini suppresses it) — no errors, no import failures

- [ ] **Step 8: Create GitHub repo and push**

```bash
git init
git add .
git commit -m "chore: project scaffold"
gh repo create tresajohn/restful-booker-py --public --source=. --remote=origin --push
gh api repos/tresajohn/restful-booker-py/pages --method POST -f build_type=workflow
```

---

### Task 2: AuthClient + Auth Tests

**Files:**
- Create: `api/auth_client.py`
- Create: `tests/conftest.py`
- Create: `tests/test_auth.py`

**Interfaces:**
- Consumes: `BASE_URL = "https://restful-booker.herokuapp.com"` (defined as a constant in conftest.py)
- Produces:
  - `AuthClient(base_url: str)` — constructor
  - `AuthClient.create_token(username: str, password: str) -> str` — returns token string; raises `ValueError("Bad credentials")` if body contains `"reason"`
  - `token` fixture (session-scoped) — returns a valid token string

- [ ] **Step 1: Write failing tests in `tests/test_auth.py`**

```python
import pytest
import allure

@allure.suite("Auth")
@allure.title("Valid credentials return a token string")
@pytest.mark.auth
def test_create_token_valid_credentials(token):
    assert isinstance(token, str)
    assert len(token) > 0

@allure.suite("Auth")
@allure.title("Invalid credentials raise ValueError")
@pytest.mark.auth
def test_create_token_invalid_credentials(auth_client):
    with pytest.raises(ValueError, match="Bad credentials"):
        auth_client.create_token("wrong", "wrong")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_auth.py -v`
Expected: ERRORS — `fixture 'token' not found` and `fixture 'auth_client' not found`

- [ ] **Step 3: Create `tests/conftest.py` with base fixtures**

```python
import pytest
from api.auth_client import AuthClient

BASE_URL = "https://restful-booker.herokuapp.com"

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def auth_client(base_url):
    return AuthClient(base_url)

@pytest.fixture(scope="session")
def token(auth_client):
    return auth_client.create_token("admin", "password123")
```

- [ ] **Step 4: Implement `AuthClient` in `api/auth_client.py`**

Signature: `AuthClient(base_url: str)` stores `self.base_url`.
`create_token(username, password) -> str`: POST `{base_url}/auth` with JSON body `{"username": username, "password": password}`, `timeout=10`, call `response.raise_for_status()`. If response JSON has key `"reason"`, raise `ValueError("Bad credentials")`. Return `response.json()["token"]`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_auth.py -v`
Expected: 2 PASSED

- [ ] **Step 6: Commit**

```bash
git add api/auth_client.py tests/conftest.py tests/test_auth.py
git commit -m "feat: auth client and tests"
```

---

### Task 3: BookingClient Read Ops + Health Tests

**Files:**
- Create: `api/booking_client.py`
- Create: `tests/test_health.py`
- Modify: `tests/test_booking.py` (create with read tests only)

**Interfaces:**
- Consumes: `base_url` fixture from `tests/conftest.py`
- Produces:
  - `BookingClient(base_url: str)` — constructor
  - `BookingClient.ping() -> int` — returns HTTP status code
  - `BookingClient.get_all() -> list[dict]` — returns list of `{"bookingid": int}`
  - `BookingClient.get_by_id(booking_id: int) -> dict` — returns booking dict; raises `requests.HTTPError` on non-2xx
  - `booking_client` fixture (session-scoped) in conftest.py

- [ ] **Step 1: Write failing tests**

`tests/test_health.py`:
```python
import pytest
import allure

@allure.suite("Health")
@allure.title("Ping returns 201")
@pytest.mark.health
def test_ping(booking_client):
    assert booking_client.ping() == 201
```

`tests/test_booking.py` (read section only):
```python
import pytest
import allure

@allure.suite("Booking")
@allure.title("Get all bookings returns a non-empty list")
@pytest.mark.booking
def test_get_all_bookings(booking_client):
    result = booking_client.get_all()
    assert isinstance(result, list)
    assert len(result) > 0
    assert "bookingid" in result[0]

@allure.suite("Booking")
@allure.title("Get booking by ID returns expected fields")
@pytest.mark.booking
def test_get_booking_by_id(booking_client):
    all_bookings = booking_client.get_all()
    first_id = all_bookings[0]["bookingid"]
    booking = booking_client.get_by_id(first_id)
    for key in ("firstname", "lastname", "totalprice", "depositpaid", "bookingdates"):
        assert key in booking
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_health.py tests/test_booking.py -v`
Expected: ERRORS — `fixture 'booking_client' not found`

- [ ] **Step 3: Add `booking_client` fixture to `tests/conftest.py`**

```python
from api.booking_client import BookingClient

@pytest.fixture(scope="session")
def booking_client(base_url):
    return BookingClient(base_url)
```

- [ ] **Step 4: Implement `BookingClient` read ops in `api/booking_client.py`**

`BookingClient(base_url: str)` stores `self.base_url`.
- `ping() -> int`: GET `{base_url}/ping`, `timeout=10`, return `response.status_code`
- `get_all() -> list[dict]`: GET `{base_url}/booking`, `timeout=10`, `raise_for_status()`, return `response.json()`
- `get_by_id(booking_id: int) -> dict`: GET `{base_url}/booking/{booking_id}`, `timeout=10`, `raise_for_status()`, return `response.json()`

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_health.py tests/test_booking.py -v`
Expected: 3 PASSED

- [ ] **Step 6: Commit**

```bash
git add api/booking_client.py tests/conftest.py tests/test_health.py tests/test_booking.py
git commit -m "feat: booking client read ops and health/read tests"
```

---

### Task 4: BookingClient Write Ops + Write Tests + Edge Cases

**Files:**
- Modify: `api/booking_client.py` (add create, update, partial_update, delete)
- Modify: `tests/conftest.py` (add booking_payload, created_booking fixtures)
- Modify: `tests/test_booking.py` (add write tests + edge cases)

**Interfaces:**
- Consumes: `booking_client`, `token` fixtures from `tests/conftest.py`
- Produces:
  - `BookingClient.create(payload: dict) -> dict` — returns `{"bookingid": int, "booking": dict}`
  - `BookingClient.update(booking_id: int, payload: dict, token: str) -> dict`
  - `BookingClient.partial_update(booking_id: int, payload: dict, token: str) -> dict`
  - `BookingClient.delete(booking_id: int, token: str) -> int` — returns status code (201)
  - `booking_payload` fixture (function-scoped) — returns a fresh booking dict
  - `created_booking` fixture (function-scoped) — yields `booking_id: int`, cleans up on teardown

- [ ] **Step 1: Write failing tests** (append to `tests/test_booking.py`)

```python
@allure.suite("Booking")
@allure.title("Create booking returns bookingid and booking fields")
@pytest.mark.booking
def test_create_booking(booking_client, booking_payload):
    result = booking_client.create(booking_payload)
    assert "bookingid" in result
    assert isinstance(result["bookingid"], int)
    assert result["booking"]["firstname"] == booking_payload["firstname"]
    # cleanup
    booking_client.delete(result["bookingid"], "")  # may 403 — that's ok, just trying

@allure.suite("Booking")
@allure.title("Full update changes all booking fields")
@pytest.mark.booking
def test_update_booking(booking_client, created_booking, booking_payload, token):
    updated_payload = {**booking_payload, "firstname": "Updated", "totalprice": 999}
    result = booking_client.update(created_booking, updated_payload, token)
    assert result["firstname"] == "Updated"
    assert result["totalprice"] == 999

@allure.suite("Booking")
@allure.title("Partial update changes only specified fields")
@pytest.mark.booking
def test_partial_update_booking(booking_client, created_booking, token):
    result = booking_client.partial_update(created_booking, {"firstname": "Patched"}, token)
    assert result["firstname"] == "Patched"

@allure.suite("Booking")
@allure.title("Delete booking returns 201 and booking no longer exists")
@pytest.mark.booking
def test_delete_booking(booking_client, created_booking, token):
    status = booking_client.delete(created_booking, token)
    assert status == 201
    import requests
    with pytest.raises(requests.HTTPError):
        booking_client.get_by_id(created_booking)

@allure.suite("Booking")
@allure.title("Get non-existent booking returns 404")
@pytest.mark.booking
def test_get_nonexistent_booking(booking_client):
    import requests
    with pytest.raises(requests.HTTPError) as exc_info:
        booking_client.get_by_id(999999999)
    assert exc_info.value.response.status_code == 404

@allure.suite("Booking")
@allure.title("Update without token returns 403")
@pytest.mark.booking
def test_update_without_token(booking_client, created_booking, booking_payload):
    import requests
    with pytest.raises(requests.HTTPError) as exc_info:
        booking_client.update(created_booking, booking_payload, "")
    assert exc_info.value.response.status_code == 403

@allure.suite("Booking")
@allure.title("Delete without token returns 403")
@pytest.mark.booking
def test_delete_without_token(booking_client, created_booking):
    import requests
    with pytest.raises(requests.HTTPError) as exc_info:
        booking_client.delete(created_booking, "")
    assert exc_info.value.response.status_code == 403
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_booking.py -v -k "create or update or delete or nonexistent"`
Expected: ERRORS — `fixture 'booking_payload' not found`, `fixture 'created_booking' not found`

- [ ] **Step 3: Add fixtures to `tests/conftest.py`**

```python
@pytest.fixture
def booking_payload():
    return {
        "firstname": "Test",
        "lastname": "User",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2025-01-01", "checkout": "2025-01-07"},
        "additionalneeds": "Breakfast",
    }

@pytest.fixture
def created_booking(booking_client, booking_payload, token):
    result = booking_client.create(booking_payload)
    booking_id = result["bookingid"]
    yield booking_id
    try:
        booking_client.delete(booking_id, token)
    except Exception:
        pass
```

- [ ] **Step 4: Implement write ops in `api/booking_client.py`**

All methods use `timeout=10` and `raise_for_status()`. Auth header: `{"Cookie": f"token={token}"}`.
- `create(payload: dict) -> dict`: POST `{base_url}/booking`, JSON body, return `response.json()`
- `update(booking_id, payload, token) -> dict`: PUT `{base_url}/booking/{booking_id}`, JSON body, auth header, `Content-Type: application/json`, `Accept: application/json`, return `response.json()`
- `partial_update(booking_id, payload, token) -> dict`: PATCH same headers as update, return `response.json()`
- `delete(booking_id, token) -> int`: DELETE `{base_url}/booking/{booking_id}`, auth header, return `response.status_code`

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v`
Expected: 12 PASSED, 0 failed

- [ ] **Step 6: Commit and push**

```bash
git add api/booking_client.py tests/conftest.py tests/test_booking.py
git commit -m "feat: booking write ops, edge cases, full suite green"
git push origin main
```

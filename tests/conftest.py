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

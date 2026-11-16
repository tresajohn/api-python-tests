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

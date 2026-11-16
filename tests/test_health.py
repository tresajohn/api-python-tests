import pytest
import allure


@allure.suite("Health")
@allure.title("Ping returns 201")
@pytest.mark.health
def test_ping(booking_client):
    assert booking_client.ping() == 201

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

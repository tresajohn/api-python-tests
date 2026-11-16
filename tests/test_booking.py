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


@allure.suite("Booking")
@allure.title("Create booking returns bookingid and booking fields")
@pytest.mark.booking
def test_create_booking(booking_client, booking_payload):
    result = booking_client.create(booking_payload)
    assert "bookingid" in result
    assert isinstance(result["bookingid"], int)
    assert result["booking"]["firstname"] == booking_payload["firstname"]


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
    import requests as req
    with pytest.raises(req.HTTPError):
        booking_client.get_by_id(created_booking)


@allure.suite("Booking")
@allure.title("Get non-existent booking returns 404")
@pytest.mark.booking
def test_get_nonexistent_booking(booking_client):
    import requests as req
    with pytest.raises(req.HTTPError) as exc_info:
        booking_client.get_by_id(999999999)
    assert exc_info.value.response.status_code == 404


@allure.suite("Booking")
@allure.title("Update without token returns 403")
@pytest.mark.booking
def test_update_without_token(booking_client, created_booking, booking_payload):
    import requests as req
    with pytest.raises(req.HTTPError) as exc_info:
        booking_client.update(created_booking, booking_payload, "")
    assert exc_info.value.response.status_code == 403


@allure.suite("Booking")
@allure.title("Delete without token returns 403")
@pytest.mark.booking
def test_delete_without_token(booking_client, created_booking):
    import requests as req
    with pytest.raises(req.HTTPError) as exc_info:
        booking_client.delete(created_booking, "")
    assert exc_info.value.response.status_code == 403

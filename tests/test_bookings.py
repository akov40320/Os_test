from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    # Для каждого теста создаём отдельное приложение с пустым хранилищем.
    with TestClient(create_app()) as test_client:
        yield test_client


def valid_booking():
    return {
        "name": "Иван Иванов",
        "phone": "+79991234567",
        "booking_date": (date.today() + timedelta(days=1)).isoformat(),
        "booking_time": "19:00",
        "guests": 2,
    }


def test_create_get_and_filter_bookings(client):
    response = client.post("/bookings", json=valid_booking())

    assert response.status_code == 201
    booking = response.json()
    assert booking["id"] == 1
    assert booking["status"] == "active"

    assert client.get("/bookings/1").json() == booking
    assert client.get("/bookings").json() == [booking]
    assert client.get(
        "/bookings", params={"date": booking["booking_date"]}
    ).json() == [booking]


def test_second_active_booking_for_same_slot_returns_409(client):
    data = valid_booking()
    assert client.post("/bookings", json=data).status_code == 201

    response = client.post("/bookings", json=data)

    assert response.status_code == 409
    assert response.json() == {"detail": "Slot is already booked"}


def test_cancel_booking_keeps_record_and_releases_slot(client):
    data = valid_booking()
    assert client.post("/bookings", json=data).status_code == 201

    response = client.delete("/bookings/1")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    assert client.get("/bookings/1").json()["status"] == "cancelled"

    replacement = client.post("/bookings", json=data)
    assert replacement.status_code == 201
    assert replacement.json()["id"] == 2


@pytest.mark.parametrize(
    "changes",
    [
        {"name": "A"},
        {"name": "A" * 51},
        {"phone": "89991234567"},
        {"guests": 0},
        {"guests": 11},
        {"booking_date": (date.today() - timedelta(days=1)).isoformat()},
        {"booking_date": (date.today() + timedelta(days=31)).isoformat()},
        {"booking_time": "11:00"},
        {"booking_time": "12:30"},
        {"booking_time": "23:00"},
    ],
)
def test_invalid_booking_data_returns_422(client, changes):
    response = client.post("/bookings", json={**valid_booking(), **changes})
    assert response.status_code == 422


@pytest.mark.parametrize("booking_time", ["12:00", "22:00"])
def test_first_and_last_allowed_hours_are_valid(client, booking_time):
    data = valid_booking()
    data["booking_time"] = booking_time
    assert client.post("/bookings", json=data).status_code == 201


def test_missing_booking_returns_404(client):
    response = client.get("/bookings/100")
    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}

    response = client.delete("/bookings/100")
    assert response.status_code == 404

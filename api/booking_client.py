import requests


class BookingClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def ping(self) -> int:
        response = requests.get(f"{self.base_url}/ping", timeout=10)
        return response.status_code

    def get_all(self) -> list[dict]:
        response = requests.get(f"{self.base_url}/booking", timeout=10)
        response.raise_for_status()
        return response.json()

    def get_by_id(self, booking_id: int) -> dict:
        response = requests.get(f"{self.base_url}/booking/{booking_id}", timeout=10)
        response.raise_for_status()
        return response.json()

    def create(self, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/booking",
            json=payload,
            headers={"Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def update(self, booking_id: int, payload: dict, token: str) -> dict:
        response = requests.put(
            f"{self.base_url}/booking/{booking_id}",
            json=payload,
            headers={
                "Cookie": f"token={token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def partial_update(self, booking_id: int, payload: dict, token: str) -> dict:
        response = requests.patch(
            f"{self.base_url}/booking/{booking_id}",
            json=payload,
            headers={
                "Cookie": f"token={token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def delete(self, booking_id: int, token: str) -> int:
        response = requests.delete(
            f"{self.base_url}/booking/{booking_id}",
            headers={"Cookie": f"token={token}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.status_code

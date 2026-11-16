import requests


class AuthClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def create_token(self, username: str, password: str) -> str:
        response = requests.post(
            f"{self.base_url}/auth",
            json={"username": username, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        body = response.json()
        if "reason" in body:
            raise ValueError("Bad credentials")
        return body["token"]

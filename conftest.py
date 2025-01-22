import pytest
import requests


MORFBOT_API_URL = "http://161.97.127.38:90/api/v1"


@pytest.fixture(scope="module")
def normal_user_token_headers() -> dict[str, str]:
    response = requests.post(
        f"{MORFBOT_API_URL}/login/access-token",
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'username': 'user@example.com',
            'password': 'password'
        })
    return response.json()

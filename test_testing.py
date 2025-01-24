import requests
from utils import delete_api_key


MORFBOT_API_URL = "http://161.97.127.38:90/api/v1"


def test_create_api_key(normal_user_token_headers: dict[str, str]) -> None:
    headers = {
        'Authorization': f"Bearer {normal_user_token_headers['access_token']}"}
    data = {"title": "pytest key test 2", "expiration_extension": "5"}

    response = requests.post(
        f"{MORFBOT_API_URL}/keys/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()

    assert content["title"] == data["title"]
    assert content["is_active"] is True
    assert "id" in content
    assert "api_key" in content
    assert "prefix_key" in content
    assert "created_at" in content
    assert "modified_at" in content
    assert "expires_at" in content
    assert content["expires_at"] is not None

    delete_api_key(id=content["id"], headers=headers)


def test_read_api_key(normal_user_token_headers: dict[str, str]) -> None:
    headers = {
        'Authorization': f"Bearer {normal_user_token_headers['access_token']}"}
    response = requests.get(
        f"{MORFBOT_API_URL}/keys/",
        headers=headers
    )
    assert response.status_code == 200
    content = response.json()

    assert len(content) > 0


def test_read_api_key_by_id(normal_user_token_headers: dict[str, str]) -> None:
    headers = {
        'Authorization': f"Bearer {normal_user_token_headers['access_token']}"}
    data = {"title": "pytest key test 2 by id", "expiration_extension": "5"}

    response = requests.post(
        f"{MORFBOT_API_URL}/keys/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    api_key_id = content["id"]
    owner_id = content["owner_id"]

    response = requests.get(
        f"{MORFBOT_API_URL}/keys/{api_key_id}",
        headers=headers
    )
    assert response.status_code == 200
    content = response.json()

    assert content["title"] == data["title"]
    assert content["is_active"] is True
    assert content["owner_id"] == owner_id

    delete_api_key(id=content["id"], headers=headers)


def test_upload_file(normal_user_token_headers):
    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json"
    }
    files = {
        "file": ("<file_name>", open("<file_path>", "rb"), "application/pdf"),
    }
    data = {
        "is_menu": "false",
        "is_private": "true",
        "org_id": "abc123",
        "auto_process": "false",
    }

    response = requests.post(
        f"{MORFBOT_API_URL}/chats/uploadfile/",
        headers=headers,
        files=files,
        data=data
    )

    assert response.status_code == 200
    response_json = response.json()

    assert "file" in response_json
    assert response_json["file"]["org_id"] == "abc567"

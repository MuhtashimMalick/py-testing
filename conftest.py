import pytest
import requests
import os

MORFBOT_API_URL = "http://161.97.127.38:90/api/v1"


@pytest.fixture(scope="module")
def normal_user_token_headers() -> dict[str, str]:
    response = requests.post(
        f"{MORFBOT_API_URL}/login/access-token",
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'username': 'constantinos@morfbot.ai',
            'password': 'morfbot_test_password'
        })
    return response.json()


@pytest.fixture
def uploaded_files(normal_user_token_headers):
    """Fixture to upload test files and return their IDs mapped by file type."""
    
    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json"
    }

    file_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "csv": "text/csv",
        "epub": "application/epub+zip"
    }


    base_path = os.path.abspath("C:/Users/User/Downloads/py-testing/py-testing/")
    
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Base path does not exist: {base_path}")

    uploaded_file_ids = {}

    for ext, mime_type in file_types.items():
        file_path = os.path.join(base_path, f"small_file.{ext}")

        if not os.path.exists(file_path):
            print(f"Skipping upload: {file_path} (file not found)")
            continue

        with open(file_path, "rb") as file:
            files = {"file": (f"small_file.{ext}", file, mime_type)}
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

            assert response.status_code == 200, f"Upload failed for {file_path}: {response.text}"

            response_json = response.json()
            assert "file" in response_json, "Response missing 'file' key"
            assert response_json["file"]["org_id"] == "abc123", "Org ID mismatch"

            file_id = response_json["file"]["id"]
            uploaded_file_ids[ext] = file_id  

    return uploaded_file_ids  
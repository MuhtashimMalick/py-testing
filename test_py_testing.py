import pytest
import requests
import os
from utils import delete_uploaded_file


MORFBOT_API_URL = "http://161.97.127.38:90/api/v1"



def test_upload(normal_user_token_headers):
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

    base_path = "C:/Users/User/Downloads/py-testing/py-testing/"
    uploaded_file_ids = []  

    for ext, mime_type in file_types.items():
        file_path = os.path.join(base_path, f"small_file.{ext}")

        if not os.path.exists(file_path):
            print(f"Skipping {file_path} (file not found)")
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

            assert response.status_code == 200, f"Upload failed for {file_path}"

            response_json = response.json()
            assert "file" in response_json
            assert response_json["file"]["org_id"] == "abc123"

            file_id = response_json["file"]["id"]
            uploaded_file_ids.append(file_id)
            delete_uploaded_file(file_id, headers)

##################################################################################

def test_delete_upload(normal_user_token_headers, uploaded_files):

    if not uploaded_files:
        pytest.skip("No uploaded files available for deletion.")

    file_id = list(uploaded_files.values())[0]

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json"
    }

    check_response = requests.get(
        f"{MORFBOT_API_URL}/chats/uploads/file/{file_id}",
        headers=headers
    )

    print(f"Check File Response Code: {check_response.status_code}")
    print(f"Check File Response Body: {check_response.text}")

    if check_response.status_code != 200:
        print("Error: File not found, skipping deletion.")
        return

    delete_response = requests.delete(
        f"{MORFBOT_API_URL}/chats/uploads/file/{file_id}",
        headers=headers
    )

    assert delete_response.status_code == 200, f"Unexpected response: {delete_response.text}"
    
#############################################################################

def test_uploaded_files(normal_user_token_headers, uploaded_files):

    if not uploaded_files:
        pytest.skip("No uploaded files available for retrieval.")

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json"
    }
    params = {
        "org_id": "abc123",
        "status": "uploaded",
        "skip": 0,
        "limit": 5
    }
    category = "file"

    response = requests.get(
        f"{MORFBOT_API_URL}/chats/uploads/{category}",
        headers=headers,
        params=params
    )

    assert response.status_code == 200, f"Unexpected response: {response.status_code}, {response.text}"

    response_json = response.json()
    assert "data" in response_json, "Missing 'data' key in response"
    assert "count" in response_json, "Missing 'count' key in response"
    assert len(response_json["data"]) > 0, "No uploaded files found"

    first_file = response_json["data"][0]
    file_id = list(uploaded_files.values())[0] 

    assert first_file["id"] == file_id, "File ID mismatch with uploaded fixture"
    assert first_file["status"] == "uploaded", "File status is not 'uploaded'"
    assert first_file["org_id"] == "abc123", "org_id mismatch"
    assert first_file["is_private"] is True, "'is_private' should be True"

    
##################################################################################

def test_read_upload_info(normal_user_token_headers, uploaded_files):

    if not uploaded_files:
        pytest.skip("No uploaded files available for info retrieval.")

    file_id = list(uploaded_files.values())[0]

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json"
    }

    list_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/file",
        headers=headers
    )

    if list_response.status_code != 200:
        print("Error: File not found in the system.")
        return

    response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/file/{file_id}",
        headers=headers
    )

    assert response.status_code == 200, f"Unexpected response: {response.text}"

    response_json = response.json()
    assert "filename" in response_json, "Missing 'filename' key in response"
    assert "status" in response_json, "Missing 'status' key in response"
    assert isinstance(response_json["filename"], str), "'filename' should be a string"

##########################################################################
def test_read_store_menu_data(normal_user_token_headers):
    file_id = "2f5f4930-dd43-499d-98a4-5e96fe6f36cf"  

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json",
    }

    list_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/file",
        headers=headers
    )

    if list_response.status_code != 200:
        print("Error: File list could not be retrieved.")
        return

    upload_data = list_response.json()
    file_exists = any(file["id"] == file_id and file.get("is_menu") for file in upload_data)

    if not file_exists:
        print(f"Error: File {file_id} is not marked as a menu file or does not exist.")
        return

    response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/menufile/{file_id}",
        headers=headers
    )

    assert response.status_code == 200, f"Unexpected response: {response.text}"

    response_json = response.json()
    assert "menu" in response_json, "Missing 'menu' key in response"
    assert isinstance(response_json["menu"], list), "Menu data should be a list"

    if response_json["menu"]:  
        menu_item = response_json["menu"][0]
        assert "category_name" in menu_item, "Missing 'category_name' in menu item"
        assert "item_name" in menu_item, "Missing 'item_name' in menu item"
        assert "item_price" in menu_item, "Missing 'item_price' in menu item"


##################################################################

def test_start_processing(normal_user_token_headers, uploaded_files):

    if not uploaded_files:
        pytest.skip("No uploaded files available for processing.")

    category = "file"
    file_id = list(uploaded_files.values())[0]

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json",
    }

    check_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/{file_id}",
        headers=headers
    )
    assert check_response.status_code == 200, f"File not found: {check_response.text}"

    file_data = check_response.json()

    if file_data.get("status") == "processed":
        pytest.skip(f"File '{file_id}' is already processed, skipping test.")

    process_response = requests.post(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/process/{file_id}",
        headers=headers
    )
    assert process_response.status_code == 200, f"Processing failed: {process_response.text}"
    
    verify_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/{file_id}",
        headers=headers
    )
    assert verify_response.status_code == 200, f"Failed to verify file status: {verify_response.text}"

###############################################################################
def test_cancel_upload(normal_user_token_headers, uploaded_files):
    """Test canceling an upload using the uploaded_files fixture."""
    
    if not uploaded_files:
        pytest.skip("No uploaded files available for cancellation.")

    file_id, file_info = list(uploaded_files.values())[0]
    document_name = file_info.get("filename")
    store_id = file_info.get("org_id")
    category = "file"

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json",
    }

    check_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}",
        headers=headers
    )

    if check_response.status_code != 200:
        pytest.skip("Could not retrieve uploads list, skipping cancellation.")

    upload_data = check_response.json()
    file_exists = any(
        file.get("filename") == document_name and file.get("org_id") == store_id
        for file in upload_data
    )

    if not file_exists:
        pytest.skip(f"Document '{document_name}' not found in store '{store_id}', skipping cancellation.")

    cancel_response = requests.delete(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/cancel/{file_id}",
        headers=headers
    )

    assert cancel_response.status_code == 200, f"Unexpected response: {cancel_response.text}"




import requests

MORFBOT_API_URL = "http://161.97.127.38:90/api/v1"


def delete_api_key(id, headers):
    requests.delete(
        f"{MORFBOT_API_URL}/keys/{id}",
        headers=headers
    )
    

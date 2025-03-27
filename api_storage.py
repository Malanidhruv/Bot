import json
import os
import datetime

CREDENTIALS_FILE = "temp_api.json"

def save_api_credentials(user_id, api_key):
    """ Save API credentials to a temporary file with a timestamp """
    data = {
        "user_id": user_id,
        "api_key": api_key,
        "date": datetime.date.today().isoformat()  # Store today's date
    }
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(data, f)

def get_api_credentials():
    """ Retrieve API credentials if they are valid for today """
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            try:
                data = json.load(f)
                if data["date"] == datetime.date.today().isoformat():
                    return data["user_id"], data["api_key"]
            except json.JSONDecodeError:
                pass  # Corrupt file, ignore
    return None, None  # If expired or missing, return None

def clear_api_credentials():
    """ Delete stored credentials (e.g., on logout) """
    if os.path.exists(CREDENTIALS_FILE):
        os.remove(CREDENTIALS_FILE)

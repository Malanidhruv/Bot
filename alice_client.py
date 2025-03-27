import os
import json
import datetime
from pya3 import Aliceblue

API_FILE = "api_credentials.json"

def save_credentials(user_id, api_key):
    """ Save AliceBlue credentials in a file for the day. """
    credentials = {
        "user_id": user_id,
        "api_key": api_key,
        "date": str(datetime.date.today())  # Store login date
    }
    with open(API_FILE, "w") as f:
        json.dump(credentials, f)

def load_credentials():
    """ Load credentials from file if they are valid for today. """
    if not os.path.exists(API_FILE):
        return None, None  # No credentials stored

    with open(API_FILE, "r") as f:
        data = json.load(f)

    # Remove credentials if they are from a past day
    if data.get("date") != str(datetime.date.today()):
        os.remove(API_FILE)  # Clear outdated credentials
        return None, None

    return data["user_id"], data["api_key"]

def initialize_alice():
    """ Initialize AliceBlue API session with stored credentials. """
    user_id, api_key = load_credentials()
    if not user_id or not api_key:
        raise Exception("AliceBlue credentials not found. Please log in.")

    alice = Aliceblue(user_id=user_id, api_key=api_key)
    alice.get_session_id()
    return alice

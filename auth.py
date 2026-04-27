# auth.py
import json
import os
import hashlib
import secrets
from datetime import datetime

USERS_FILE    = "data/users.json"
PROGRESS_FILE = "data/progress.json"


def _ensure_data_dir():
    os.makedirs("data", exist_ok=True)


def _load_users():
    _ensure_data_dir()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}


def _save_users(users):
    _ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _hash_password(password, salt):
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def register_user(username, password):
    username = username.strip().lower()
    if not username or len(username) < 3:
        return {"success": False, "error": "Username must be at least 3 characters."}
    if not password or len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}
    users = _load_users()
    if username in users:
        return {"success": False, "error": "Username already exists. Please log in."}
    salt  = secrets.token_hex(16)
    users[username] = {
        "password_hash": _hash_password(password, salt),
        "salt":          salt,
        "joined":        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "level":         "beginner",
    }
    _save_users(users)
    return {"success": True}


def login_user(username, password):
    username = username.strip().lower()
    users    = _load_users()
    if username not in users:
        return {"success": False, "error": "Username not found. Please register first."}
    user      = users[username]
    hashed_pw = _hash_password(password, user["salt"])
    if hashed_pw != user["password_hash"]:
        return {"success": False, "error": "Incorrect password."}
    return {"success": True, "username": username}


def get_user_level(username):
    users = _load_users()
    return users.get(username, {}).get("level", "beginner")


def update_user_level(username, level):
    users = _load_users()
    if username in users:
        users[username]["level"] = level
        _save_users(users)


def _load_progress():
    _ensure_data_dir()
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {}


def _save_progress(progress):
    _ensure_data_dir()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, default=str)


def save_session(username, session_data):
    progress = _load_progress()
    if username not in progress:
        progress[username] = {"sessions": []}
    session_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    progress[username]["sessions"].append(session_data)
    _save_progress(progress)


def get_user_progress(username):
    progress = _load_progress()
    return progress.get(username, {"sessions": []})


def get_all_users():
    return list(_load_users().keys())

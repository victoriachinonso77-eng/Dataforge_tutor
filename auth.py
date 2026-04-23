"""
auth.py — Simple username/password authentication with JSON storage.
Handles user registration, login, and session management.
"""

import json
import os
import hashlib
import secrets
from datetime import datetime
from pathlib import Path

# ─── Storage paths ────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
PROGRESS_FILE = DATA_DIR / "progress.json"

DATA_DIR.mkdir(exist_ok=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _hash_password(password: str, salt: str) -> str:
    """SHA-256 hash with salt."""
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def _load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save_json(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─── User management ──────────────────────────────────────────────────────────

def register_user(username: str, password: str, display_name: str = "") -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success: bool, message: str)
    """
    if not username.strip() or not password.strip():
        return False, "Username and password cannot be empty."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    users = _load_json(USERS_FILE)

    if username.lower() in [u.lower() for u in users]:
        return False, "Username already exists. Please choose another."

    salt = secrets.token_hex(16)
    users[username] = {
        "display_name": display_name or username,
        "password_hash": _hash_password(password, salt),
        "salt": salt,
        "created_at": datetime.now().isoformat(),
    }
    _save_json(USERS_FILE, users)
    return True, "Account created successfully!"


def login_user(username: str, password: str) -> tuple[bool, str, dict]:
    """
    Authenticate a user.
    Returns (success: bool, message: str, user_data: dict)
    """
    if not username.strip() or not password.strip():
        return False, "Please enter both username and password.", {}

    users = _load_json(USERS_FILE)

    # Case-insensitive username lookup
    matched_key = next((k for k in users if k.lower() == username.lower()), None)
    if not matched_key:
        return False, "Username not found.", {}

    user = users[matched_key]
    hashed = _hash_password(password, user["salt"])

    if hashed != user["password_hash"]:
        return False, "Incorrect password.", {}

    return True, f"Welcome back, {user['display_name']}!", {
        "username": matched_key,
        "display_name": user["display_name"],
        "created_at": user["created_at"],
    }


# ─── Progress storage ─────────────────────────────────────────────────────────

def save_session_result(username: str, result: dict):
    """
    Save a completed quiz session result for a user.
    result should contain: score, max_score, percentage, badge,
                           difficulty, mastered_concepts, weak_concepts, summary
    """
    progress = _load_json(PROGRESS_FILE)

    if username not in progress:
        progress[username] = {"sessions": []}

    session = {
        "timestamp": datetime.now().isoformat(),
        "score": result.get("total_score", 0),
        "max_score": result.get("max_score", 0),
        "percentage": result.get("percentage", 0),
        "badge": result.get("badge", ""),
        "difficulty": result.get("difficulty", ""),
        "mastered_concepts": result.get("mastered_concepts", []),
        "weak_concepts": result.get("weak_concepts", []),
        "summary": result.get("summary", ""),
    }

    progress[username]["sessions"].append(session)
    _save_json(PROGRESS_FILE, progress)


def get_user_progress(username: str) -> dict:
    """
    Load all progress for a user.
    Returns dict with sessions list and computed stats.
    """
    progress = _load_json(PROGRESS_FILE)
    user_data = progress.get(username, {"sessions": []})
    sessions = user_data["sessions"]

    if not sessions:
        return {"sessions": [], "stats": None}

    # Compute aggregate stats
    scores = [s["percentage"] for s in sessions]
    all_mastered = [c for s in sessions for c in s.get("mastered_concepts", [])]
    all_weak = [c for s in sessions for c in s.get("weak_concepts", [])]

    # Most common concepts
    from collections import Counter
    mastered_counts = Counter(all_mastered)
    weak_counts = Counter(all_weak)

    stats = {
        "total_sessions": len(sessions),
        "average_score": round(sum(scores) / len(scores), 1),
        "best_score": max(scores),
        "latest_score": scores[-1],
        "top_mastered": [c for c, _ in mastered_counts.most_common(3)],
        "top_weak": [c for c, _ in weak_counts.most_common(3)],
        "improvement": round(scores[-1] - scores[0], 1) if len(scores) > 1 else 0,
    }

    return {"sessions": sessions, "stats": stats}
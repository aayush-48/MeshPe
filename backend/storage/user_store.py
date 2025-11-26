import json
import os
from typing import Dict, Optional

STORAGE_DIR = os.path.join(os.path.dirname(__file__))
USERS_FILE = os.path.join(STORAGE_DIR, "users.json")


def _load_raw() -> Dict[str, dict]:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_raw(data: Dict[str, dict]) -> None:
    os.makedirs(STORAGE_DIR, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_user(user_id: str) -> Optional[dict]:
    users = _load_raw()
    return users.get(user_id)


def create_or_update_user(user_id: str, name: str, phone: str, language: str) -> dict:
    users = _load_raw()
    user = users.get(user_id, {})
    user.update(
        {
            "id": user_id,
            "name": name,
            "phone": phone,
            "language": language,
        }
    )
    users[user_id] = user
    _save_raw(users)
    return user


def list_contacts(user_id: str):
    users = _load_raw()
    user = users.get(user_id) or {}
    return user.get("contacts", [])


def add_contact(user_id: str, contact_name: str, contact_id: str):
    users = _load_raw()
    user = users.setdefault(
        user_id,
        {
            "id": user_id,
            "name": "",
            "phone": "",
            "language": "english",
        },
    )
    contacts = user.setdefault("contacts", [])
    contacts.append({"name": contact_name, "id": contact_id})
    _save_raw(users)
    return contacts



"""In-memory user store for the sandbox.

No database — users reset on every restart, matching the note store's behaviour.
"""
from __future__ import annotations

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

_users_by_id: dict[int, "User"] = {}
_users_by_name: dict[str, int] = {}
_next_id = 1


def reset_store() -> None:
    """Clear all users — called between tests to prevent state bleed."""
    global _next_id
    _users_by_id.clear()
    _users_by_name.clear()
    _next_id = 1


class User(UserMixin):
    def __init__(self, id: int, username: str, password_hash: str) -> None:
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create(cls, username: str, password: str) -> "User | None":
        """Return the new User, or None if the username is already taken."""
        global _next_id
        if username in _users_by_name:
            return None
        user = cls(_next_id, username, generate_password_hash(password))
        _users_by_id[_next_id] = user
        _users_by_name[username] = _next_id
        _next_id += 1
        return user

    @staticmethod
    def get(user_id: int) -> "User | None":
        return _users_by_id.get(user_id)

    @staticmethod
    def get_by_username(username: str) -> "User | None":
        uid = _users_by_name.get(username)
        return _users_by_id.get(uid) if uid is not None else None

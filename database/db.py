"""Database helpers for Yuki bot."""
from __future__ import annotations


from pymongo import MongoClient
from pymongo.collection import Collection
from config import MONGO_URI, DB_NAME


_client = MongoClient(MONGO_URI)
_db = _client[DB_NAME]
_users = _db["users"]


def get_users_collection() -> Collection:
    return _users


def init_db() -> None:
    _users.create_index("user_id", unique=True)

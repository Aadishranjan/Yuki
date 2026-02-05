"""Database helpers for Yuki bot."""
from __future__ import annotations


from pymongo import MongoClient
from pymongo.collection import Collection
from config import MONGO_URI, DB_NAME


_client = MongoClient(MONGO_URI)
_db = _client[DB_NAME]
_users = _db["users"]
_sudoers = _db["sudoers"]
_groups = _db["groups"]


def get_users_collection() -> Collection:
    return _users

def get_sudoers_collection() -> Collection:
    return _sudoers

def get_groups_collection() -> Collection:
    return _groups


def init_db() -> None:
    _users.create_index("user_id", unique=True)
    _sudoers.create_index("user_id", unique=True)
    _groups.create_index("chat_id", unique=True)

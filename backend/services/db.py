"""MongoDB client + collections."""
from __future__ import annotations

import os
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_db() -> Database:
    global _client, _db
    if _db is None:
        mongo_url = os.environ["MONGO_URL"]
        db_name = os.environ["DB_NAME"]
        _client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        _db = _client[db_name]
        _ensure_indexes(_db)
    return _db


def _ensure_indexes(db: Database) -> None:
    db.gallery_entries.create_index("id", unique=True)
    db.gallery_entries.create_index([("created_at", -1)])
    db.chat_sessions.create_index("session_id", unique=True)
    db.system_state.create_index("key", unique=True)
    db.presets.create_index("id", unique=True)
    db.presets.create_index([("created_at", -1)])


def gallery_col() -> Collection:
    return get_db().gallery_entries


def sessions_col() -> Collection:
    return get_db().chat_sessions


def state_col() -> Collection:
    return get_db().system_state


def presets_col() -> Collection:
    return get_db().presets

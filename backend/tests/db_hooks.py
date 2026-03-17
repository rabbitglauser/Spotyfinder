from __future__ import annotations

from typing import Any


def initialize_database(database_url: str) -> Any:
    """
    Project integration point.

    Replace this with your DB bootstrap logic (engine creation, migrations,
    schema setup, etc.) and return a handle used by `create_session`.
    """
    return {"database_url": database_url}


def create_session(db_handle: Any) -> Any:
    """
    Project integration point.

    Replace this with your session/connection factory and return the object
    your CRUD tests should use.
    """
    return db_handle


def cleanup_database(db_handle: Any) -> None:
    """
    Project integration point.

    Replace this with cleanup logic (drop schema, close engine, rollback, etc.).
    """
    _ = db_handle

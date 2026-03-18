from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from fastapi import HTTPException
from psycopg import Error as PsycopgError
from psycopg import OperationalError
from psycopg import connect
from psycopg.rows import dict_row

app = FastAPI()


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured.")
    return database_url


def _fetch_items(database_url: str) -> list[dict[str, Any]]:
    with connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    track_uri,
                    track_name,
                    artist_name,
                    album_name,
                    popularity,
                    explicit,
                    added_at
                FROM incoming_tracks
                ORDER BY id;
                """
            )
            return [dict(row) for row in cursor.fetchall()]


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Backend is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/items")
def get_items() -> dict[str, list[dict[str, Any]]]:
    database_url = _get_database_url()

    try:
        items = _fetch_items(database_url)
    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is not reachable.",
        ) from exc
    except PsycopgError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database query failed.",
        ) from exc

    return {"items": items}

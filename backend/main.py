<<<<<<< HEAD
from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from fastapi import HTTPException
from psycopg import Error as PsycopgError
from psycopg import OperationalError
from psycopg import connect
from psycopg.rows import dict_row
=======
import os

import pymysql
from fastapi import FastAPI, HTTPException
from pymysql.cursors import DictCursor
from pymysql.err import InterfaceError, MySQLError, OperationalError
>>>>>>> bdbb1769 (oddycommit)

app = FastAPI()


<<<<<<< HEAD
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
=======
@app.get("/")
def root():
>>>>>>> bdbb1769 (oddycommit)
    return {"message": "Backend is running"}


@app.get("/health")
<<<<<<< HEAD
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
=======
def health():
    return {"status": "ok"}


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "spotyfinderdb"),
        "cursorclass": DictCursor,
        "autocommit": True,
    }


@app.get("/api/items")
def get_items():
    try:
        with pymysql.connect(**get_db_config()) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        t.id,
                        t.track_uri,
                        t.duration_ms,
                        t.popularity,
                        t.explicit,
                        a.name AS album_name
                    FROM tracks AS t
                    LEFT JOIN albums AS a ON a.id = t.album_id
                    LIMIT 50
                """)
                items = cursor.fetchall()

        return {"count": len(items), "items": items}

    except (OperationalError, InterfaceError):
        raise HTTPException(status_code=503, detail="Database is not reachable")
    except MySQLError:
        raise HTTPException(status_code=500, detail="Database query failed")
>>>>>>> bdbb1769 (oddycommit)

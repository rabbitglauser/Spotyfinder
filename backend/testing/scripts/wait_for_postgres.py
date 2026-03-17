from __future__ import annotations

import os
import time

import psycopg


def _to_psycopg_url(database_url: str) -> str:
    return database_url.replace("+psycopg", "")


def main() -> None:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        raise SystemExit("TEST_DATABASE_URL is required.")

    connect_url = _to_psycopg_url(database_url)
    timeout_seconds = int(os.getenv("POSTGRES_WAIT_TIMEOUT", "60"))
    deadline = time.time() + timeout_seconds

    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with psycopg.connect(connect_url, connect_timeout=3) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1;")
                    cursor.fetchone()
            return
        except Exception as exc:  # pragma: no cover - best effort wait helper
            last_error = exc
            time.sleep(2)

    raise SystemExit(f"Postgres was not ready in {timeout_seconds}s: {last_error}")


if __name__ == "__main__":
    main()

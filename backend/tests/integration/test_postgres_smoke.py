from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def _to_psycopg_url(database_url: str) -> str:
    return database_url.replace("+psycopg", "")


def test_can_connect_to_postgres(test_database_url: str) -> None:
    if not test_database_url.startswith("postgresql"):
        pytest.skip("TEST_DATABASE_URL is not a PostgreSQL URL.")

    psycopg = pytest.importorskip("psycopg")

    with psycopg.connect(_to_psycopg_url(test_database_url)) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            assert cursor.fetchone() == (1,)

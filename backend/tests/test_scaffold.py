from __future__ import annotations


def test_database_url_fixture_returns_value(test_database_url: str) -> None:
    assert isinstance(test_database_url, str)
    assert test_database_url


def test_db_session_fixture_is_available(db_session: object) -> None:
    assert db_session is not None


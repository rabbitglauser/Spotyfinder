from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from typing import Generator

import pytest

from tests import db_hooks


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--db-url",
        action="store",
        default=None,
        help="Database URL for tests. Overrides TEST_DATABASE_URL.",
    )
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests marked with @pytest.mark.integration.",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.getoption("--integration"):
        return

    skip_marker = pytest.mark.skip(
        reason="integration tests are disabled by default. Use --integration."
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def test_database_url(pytestconfig: pytest.Config, project_root: Path) -> str:
    cli_value = pytestconfig.getoption("--db-url")
    if cli_value:
        return str(cli_value)

    env_value = os.getenv("TEST_DATABASE_URL")
    if env_value:
        return env_value

    sqlite_dir = project_root / "tests" / ".tmp"
    sqlite_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path = sqlite_dir / "test.db"
    return f"sqlite:///{sqlite_path.as_posix()}"


@pytest.fixture(scope="session")
def db_handle(test_database_url: str) -> Generator[Any, None, None]:
    handle = db_hooks.initialize_database(test_database_url)
    try:
        yield handle
    finally:
        db_hooks.cleanup_database(handle)


@pytest.fixture()
def db_session(db_handle: Any) -> Generator[Any, None, None]:
    session = db_hooks.create_session(db_handle)
    try:
        yield session
    finally:
        close = getattr(session, "close", None)
        if callable(close):
            close()


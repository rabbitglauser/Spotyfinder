# Testing Setup

This backend now includes two test execution paths:

- Local test run with SQLite defaults (fast feedback).
- Docker integration run with Postgres (real DB behavior).

## Install test dependencies

From `backend/`:

```bash
python -m pip install -r requirements-test.txt
```

## Run tests locally (SQLite)

From `backend/`:

```bash
python -m pytest -m "not integration"
```

Or via scripts:

- `testing/scripts/run-local-tests.sh`
- `testing/scripts/run-local-tests.cmd`

You can override the database URL:

```bash
TEST_DATABASE_URL=sqlite:///./tests/.tmp/custom.db python -m pytest -m "not integration"
```

## Run integration tests with Docker (Postgres)

From `backend/`:

```bash
docker compose -f testing/docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from tests
```

Or via scripts:

- `testing/scripts/run-docker-tests.sh`
- `testing/scripts/run-docker-tests.cmd`

## How to plug into your existing DB/session layer

Edit `tests/db_hooks.py`:

- `initialize_database(database_url)` for engine/bootstrap setup.
- `create_session(db_handle)` to return your session/connection object.
- `cleanup_database(db_handle)` for teardown.

Your tests then consume the `db_session` fixture from `tests/conftest.py`.

## Marker behavior

- Integration tests should use `@pytest.mark.integration`.
- They are skipped by default.
- To run them directly without Docker:

```bash
python -m pytest --integration -m integration
```


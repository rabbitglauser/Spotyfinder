#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BACKEND_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

cd "$BACKEND_DIR"

if [ -z "${TEST_DATABASE_URL:-}" ]; then
  TEST_DATABASE_URL="sqlite:///./tests/.tmp/test.db"
fi

export TEST_DATABASE_URL

PYTHON_BIN="python"
if [ -x ".venv/Scripts/python.exe" ]; then
  PYTHON_BIN=".venv/Scripts/python.exe"
elif [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
fi

"$PYTHON_BIN" -m pytest -m "not integration" "$@"

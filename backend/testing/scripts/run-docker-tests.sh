#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BACKEND_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$BACKEND_DIR/testing/docker-compose.test.yml"

cleanup() {
  docker compose -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
}

trap cleanup EXIT

docker compose -f "$COMPOSE_FILE" up --build --abort-on-container-exit --exit-code-from tests


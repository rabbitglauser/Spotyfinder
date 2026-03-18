#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

DOCKERHUB_USERNAME=${DOCKERHUB_USERNAME:-rabbitglauser}
BACKEND_IMAGE=${BACKEND_IMAGE:-${DOCKERHUB_USERNAME}/docker-backend}
FRONTEND_IMAGE=${FRONTEND_IMAGE:-${DOCKERHUB_USERNAME}/docker-frontend}
IMAGE_TAG=${IMAGE_TAG:-latest}
PUSH_LATEST=${PUSH_LATEST:-false}

if [ -n "${DOCKERHUB_TOKEN:-}" ]; then
  echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
fi

build_and_push() {
  image=$1
  dockerfile=$2

  echo "Building ${image}:${IMAGE_TAG} from ${dockerfile}"
  docker build -f "$dockerfile" -t "${image}:${IMAGE_TAG}" .

  if [ "$PUSH_LATEST" = "true" ] && [ "$IMAGE_TAG" != "latest" ]; then
    docker tag "${image}:${IMAGE_TAG}" "${image}:latest"
  fi

  echo "Pushing ${image}:${IMAGE_TAG}"
  docker push "${image}:${IMAGE_TAG}"

  if [ "$PUSH_LATEST" = "true" ] && [ "$IMAGE_TAG" != "latest" ]; then
    echo "Pushing ${image}:latest"
    docker push "${image}:latest"
  fi
}

build_and_push "$BACKEND_IMAGE" "backend/Dockerfile"
build_and_push "$FRONTEND_IMAGE" "frontend/Dockerfile"

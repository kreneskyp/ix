DOCKER_COMPOSE=docker-compose.yml
DOCKERFILE=Dockerfile
DOCKER_REGISTRY=ghcr.io
DOCKER_REPOSITORY=${DOCKER_REGISTRY}/ix/sandbox
HASH_FILES=requirements*.txt package.json Dockerfile
IMAGE_TAG=$(shell cat $(HASH_FILES) | md5sum | cut -d ' ' -f 1)
IMAGE_URL=$(DOCKER_REPOSITORY):$(IMAGE_TAG)
IMAGE_SENTINEL=.sentinel/image

DOCKER_COMPOSE_RUN=docker-compose run --rm sandbox
DOCKER_COMPOSE_RUN_WITH_PORT=docker-compose run -p 8000:8000 --rm sandbox

# set to skip build, primarily used by github workflows to skip builds when image is cached
NO_IMAGE_BUILD?=0


.PHONY: image-tag
image-tag:
	@echo ${IMAGE_TAG}


.PHONY: image-url
image-url:
	@echo ${IMAGE_URL}


# build existence check
.sentinel:
	mkdir -p .sentinel

# inner build target for image
${IMAGE_SENTINEL}: .sentinel $(HASH_FILES)
ifneq (${NO_IMAGE_BUILD}, 1)
	echo building ${IMAGE_URL}
	docker build -t ${IMAGE_URL} -f $(DOCKERFILE) .
	docker tag ${IMAGE_URL} ${DOCKER_REPOSITORY}:latest
	touch $@
endif

# setup target for docker-compose, add deps here to apply to all compose sessions
.PHONY: compose
compose: image

# =========================================================
# Build
# =========================================================

# dev setup - runs all initial setup steps in one go
.PHONY: dev_setup
dev_setup: image frontend migrate dev_fixtures

# build image
.PHONY: image
image: ${IMAGE_SENTINEL}

# full frontend build
.PHONY: frontend
frontend: compose graphene_to_graphql compile_relay webpack

# compile javascript
.PHONY: webpack
webpack: compose
	docker-compose run --rm sandbox webpack --progress

# compile javascript in watcher mode
.PHONY: webpack-watch
webpack-watch: compose
	${DOCKER_COMPOSE_RUN} webpack --progress --watch

# compile graphene graphql classes into schema.graphql for javascript
.PHONY: graphene_to_graphql
graphene_to_graphql: compose
	docker-compose run --rm sandbox ./manage.py graphql_schema --out ./frontend/schema.graphql

# compile javascript
.PHONY: compile_relay
compile_relay: compose
	docker-compose run --rm sandbox npm run relay


# =========================================================
# Run
# =========================================================

# run backend and frontend
.PHONY: runserver
runserver: compose
	${DOCKER_COMPOSE_RUN_WITH_PORT} ./manage.py runserver 0.0.0.0:8000

# run worker
.PHONY: worker
worker: compose
	${DOCKER_COMPOSE_RUN} celery.sh

# =========================================================
# Shells
# =========================================================

.PHONY: bash
bash: compose
	${DOCKER_COMPOSE_RUN} /bin/bash

.PHONY: shell
shell: compose
	${DOCKER_COMPOSE_RUN} ./manage.py shell_plus

# =========================================================
# Dev tools
# =========================================================

# shortcut to run django migrations
.PHONY: migrate
migrate: compose
	${DOCKER_COMPOSE_RUN} ./manage.py migrate

# shortcut to generate django migrations
.PHONY: migrations
migrations: compose
	${DOCKER_COMPOSE_RUN} ./manage.py makemigrations

# load initial data needed for dev environment
.PHONY: dev_fixtures
dev_fixtures: compose
	${DOCKER_COMPOSE_RUN} ./manage.py loaddata dev_data.json


# =========================================================
# Testing
# =========================================================

.PHONY: test
test: compose pytest

.PHONY: lint
test: compose flake8 black-check

.PHONY: format
format: black isort

.PHONY: black
black: compose
	${DOCKER_COMPOSE_RUN} black .

.PHONY: black-check
black-check: compose
	${DOCKER_COMPOSE_RUN} black --check .

.PHONY: flake8
flake8: compose
	${DOCKER_COMPOSE_RUN} flake8 .

.PHONY: isort
isort: compose
	${DOCKER_COMPOSE_RUN} isort .

.PHONY: pytest
pytest: compose
	${DOCKER_COMPOSE_RUN} pytest

.PHONY: pyright
pyright: compose
	${DOCKER_COMPOSE_RUN} pyright



# =========================================================
# Cleanup
# =========================================================

.PHONY: clean
clean:
	rm -rf .sentinel
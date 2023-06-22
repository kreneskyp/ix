DOCKER_COMPOSE=docker-compose.yml
DOCKER_REGISTRY=ghcr.io

# check for md5sum or md5 for hashing
HASHER := $(shell command -v md5sum 2> /dev/null)
ifndef HASHER
    HASHER := md5 -r
endif

# APP IMAGE
DOCKERFILE=Dockerfile
DOCKER_REPOSITORY=${DOCKER_REGISTRY}/kreneskyp/ix/sandbox
HASH_FILES=requirements*.txt package.json Dockerfile
IMAGE_TAG=$(shell cat $(HASH_FILES) | ${HASHER} | cut -d ' ' -f 1)
IMAGE_URL=$(DOCKER_REPOSITORY):$(IMAGE_TAG)
IMAGE_SENTINEL=.sentinel/image

# PSQL IMAGE
DOCKERFILE_PSQL=psql.Dockerfile
DOCKER_REPOSITORY_PSQL=${DOCKER_REGISTRY}/kreneskyp/ix/postgres-pg-vector
HASH_FILES_PSQL=psql.Dockerfile
IMAGE_TAG_PSQL=$(shell cat $(HASH_FILES_PSQL) | ${HASHER} | cut -d ' ' -f 1)
IMAGE_URL_PSQL=$(DOCKER_REPOSITORY_PSQL):$(IMAGE_TAG_PSQL)
IMAGE_SENTINEL_PSQL=.sentinel/image.psql

DOCKER_COMPOSE_RUN=docker-compose run --rm web
DOCKER_COMPOSE_RUN_WITH_PORT=docker-compose run -p 8000:8000 --rm web

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

# inner build target for sandbox image
${IMAGE_SENTINEL}: .sentinel $(HASH_FILES)
ifneq (${NO_IMAGE_BUILD}, 1)
	echo building ${IMAGE_URL}
	docker build -t ${IMAGE_URL} -f $(DOCKERFILE) .
	docker tag ${IMAGE_URL} ${DOCKER_REPOSITORY}:latest
	touch $@
endif

# inner build target for postgres image
${IMAGE_SENTINEL_PSQL}: .sentinel $(HASH_FILES_PSQL)
ifneq (${NO_IMAGE_BUILD}, 1)
	echo building ${IMAGE_URL_PSQL}
	docker build -t ${IMAGE_URL_PSQL} -f $(DOCKERFILE_PSQL) .
	docker tag ${IMAGE_URL_PSQL} ${DOCKER_REPOSITORY_PSQL}:latest
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
image: ${IMAGE_SENTINEL} ${IMAGE_SENTINEL_PSQL}

# full frontend build
.PHONY: frontend
frontend: compose npm_install graphene_to_graphql compile_relay webpack

# install npm packages
.PHONY: npm_install
npm_install: compose package.json
	docker-compose run --rm web npm install

# compile javascript
.PHONY: webpack
webpack: compose
	${DOCKER_COMPOSE_RUN} webpack --progress

# compile javascript in watcher mode
.PHONY: webpack-watch
webpack-watch: compose
	${DOCKER_COMPOSE_RUN} webpack --progress --watch

# compile graphene graphql classes into schema.graphql for javascript
.PHONY: graphene_to_graphql
graphene_to_graphql: compose
	${DOCKER_COMPOSE_RUN} ./manage.py graphql_schema --out ./frontend/schema.graphql

# compile javascript
.PHONY: compile_relay
compile_relay: compose
	${DOCKER_COMPOSE_RUN} npm run relay


# =========================================================
# Run
# =========================================================

# run backend and frontend. This starts uvicorn for asgi+websockers
# and nginx to serve static files
.PHONY: server
server: compose
	docker-compose up web nginx


# run django debug server, backup in case nginx ever breaks
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
	${DOCKER_COMPOSE_RUN} ./manage.py loaddata fake_user node_types
	# use management commands for now since fixtures didn't load correctly
	${DOCKER_COMPOSE_RUN} ./manage.py create_moderator_v1
	${DOCKER_COMPOSE_RUN} ./manage.py create_coder_v1
	# ${DOCKER_COMPOSE_RUN} ./manage.py create_planner_v3
	# ${DOCKER_COMPOSE_RUN} ./manage.py create_dad_jokes_v1
	# ${DOCKER_COMPOSE_RUN} ./manage.py create_pirate_v1



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
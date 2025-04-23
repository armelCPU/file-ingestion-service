.DEFAULT_GOAL := help
SHELL := /bin/bash

# identity and project variables
HOST_UID := $(shell id -u)
HOST_GID := $(shell id -g)
PROJECT_NAME := rag-app

# Docker Compose
DOCKER_COMPOSE_FILE := docker-compose.yml
DOCKER_COMPOSE_CMD := HOST_UID=$(HOST_UID) HOST_GID=$(HOST_GID) DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f $(DOCKER_COMPOSE_FILE) --project-name $(PROJECT_NAME)

# Default command in a container
COMMAND := /bin/bash

# --- Commandes ---

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} \
	/^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: docker-build
docker-build: ## Build all containers
	$(DOCKER_COMPOSE_CMD) build

.PHONY: docker-up
docker-up: ## Start all containers
	$(DOCKER_COMPOSE_CMD) up -d

.PHONY: docker-down
docker-down: ## Stop and remove containers
	$(DOCKER_COMPOSE_CMD) down

.PHONY: docker-logs
docker-logs: ## View logs from all containers
	$(DOCKER_COMPOSE_CMD) logs -f

.PHONY: docker-logs-api
docker-logs-api: ## View logs from the API container
	$(DOCKER_COMPOSE_CMD) logs -f backend

.PHONY: docker-logs-celery
docker-logs-celery: ## View logs from the Celery container
	$(DOCKER_COMPOSE_CMD) logs -f celery

.PHONY: docker-ps
docker-ps: ## List running containers
	$(DOCKER_COMPOSE_CMD) ps

.PHONY: docker-exec
docker-exec: ## Execute a command in a container (ex: make docker-exec CONTAINER=backend COMMAND="ls")
	$(DOCKER_COMPOSE_CMD) exec $(CONTAINER) $(COMMAND)

.PHONY: docker-restart
docker-restart: ## Restart a specific container
	$(DOCKER_COMPOSE_CMD) restart $(CONTAINER)

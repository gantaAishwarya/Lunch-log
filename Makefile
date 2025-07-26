start: ## Start the docker containers
	@echo "Starting the docker containers"
	@docker compose up
	@echo "Containers started - http://localhost:8000"

start-build: ## Rebuild and start the docker containers
	@echo "Re-Building and starting the docker containers"
	@docker compose up --build
	@echo "Containers started - http://localhost:8000"

stop: ## Stop Containers
	@docker compose down

restart: stop start ## Restart Containers

start-bg:  ## Run containers in the background
	@docker compose up -d

follow:  ## Follow logs of containers running in the background
	@docker compose logs --follow

build: ## Build Containers
	@docker compose build

ssh: ## SSH into running web container
	docker compose exec web bash

migrations: ## Create DB migrations in the container
	@docker compose exec web python3 manage.py makemigrations

migrate: ## Run DB migrations in the container
	@docker compose exec web python3 manage.py migrate

super:  ## Create a Django admin account
	@docker compose exec web python manage.py createsuperuser

shell: ## Get a Django shell
	@docker compose exec web python manage.py shell_plus

dbshell: ## Get a Database shell
	@docker compose exec db psql -U postgres admin

test: ## Run Django tests
	@docker compose exec web python3 manage.py pytest --cov=backend.apps --cov-report=term-missing

.PHONY: help
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
SHELL := /bin/bash

.PHONY: $(SERVICES) logs

## NOTE: Add this to your .bashrc to enable make target tab completion
##    complete -W "\`grep -oE '^[a-zA-Z0-9_.-]+:([^=]|$)' ?akefile | sed 's/[^a-zA-Z0-9_.-]*$//'\`" make
## Reference: https://stackoverflow.com/a/38415982

help: ## This info
	@echo '_________________'
	@echo '| Make targets: |'
	@echo '-----------------'
	@echo
	@cat Makefile | grep -E '^[a-zA-Z\/_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo


build: ## build the docker image
	docker build -t cast-iron/worker .

nag: sort lint type test ## Run all checks

lint: ## Run pylint over the main project files
	poetry run pylint etl

sort: ## Sort files
	poetry run isort -rc etl tests

test: ## Run integration tests
	poetry run coverage run --source etl -m pytest
	poetry run coverage report -m
	poetry run coverage html -d tests/htmlcov

type: ## Run mypy
	poetry run mypy etl --ignore-missing-imports --follow-imports=skip

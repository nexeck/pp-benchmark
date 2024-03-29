.DEFAULT_GOAL:=help
SHELL:=/usr/bin/env bash

##@ Helpers

.PHONY: help

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z\/_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Dependencies

.PHONY: deps

deps:  ## Check dependencies
	@pipenv --version

##@ PP Realestate

.PHONY: run

install: ##Install
	(pipenv install $(ARGS))

update: ##Update
	(pipenv update)

run: ##Run
	(pipenv run python main.py $(ARGS))

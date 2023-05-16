
.PHONY: help
help: ## show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: init
init: ## init the project
	@poetry install

.PHONY: test
test: ## run tests
	@poetry run coverage run --source="cumulus" -m unittest discover tests && poetry run coverage report

.PHONY: lint
lint: ## run flake8 linter
	@poetry run flake8 cumulus

.PHONY: build
build: ## package the module
	@poetry build

.PHONY: upload
upload: ## upload the package to PyPi
	@poetry publish

.PHONY: all
all: lint test build upload ## lint, test, build, and upload the package to PyPI

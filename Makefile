new_hash = $(shell sha2 -256 -q Pipfile)
old_hash = $(shell cat pipfile_hash)
PIPENV_VENV_IN_PROJECT = 1
PROJECT_NAME = yaml_anchor_generator
PYTHON_CMD = pipenv run python

.PHONY: default
default: lint

.PHONY: setup
setup:
	if ! pipenv --venv; then PIPENV_VENV_IN_PROJECT=$(PIPENV_VENV_IN_PROJECT) pipenv install --dev; fi

.PHONY: update
update: setup
	if [[ "$(new_hash)" != "$(old_hash)" ]]; then PIPENV_VENV_IN_PROJECT=$(PIPENV_VENV_IN_PROJECT) pipenv update --dev; echo "$(new_hash)" > pipfile_hash; fi

.PHONY: lint
lint: update
	pipenv run autoflake -i -r --imports $(PROJECT_NAME) $(PROJECT_NAME)
	pipenv run black $(PROJECT_NAME)
	pipenv run flake8 $(PROJECT_NAME)
	pipenv run mypy --strict -p $(PROJECT_NAME)

.PHONY: test
test: update
	pipenv run pytest --cov=$(PROJECT_NAME) $(PROJECT_NAME)
	pipenv run coverage xml -i

.PHONY: dump
dump:
	$(PYTHON_CMD) -c 'import $(PROJECT_NAME).dump as dump; s = dump.parent_to_string(dump.sample, {}, 0); print(s)'

.DEFAULT_GOAL := help
RELEASE_BRANCHES ?= main master
REMOTE ?= origin

VENV_PYTHON_WIN := .venv/Scripts/python.exe
VENV_PYTHON_POSIX := .venv/bin/python

ifneq ($(wildcard $(VENV_PYTHON_WIN)),)
PYTHON ?= $(VENV_PYTHON_WIN)
else ifneq ($(wildcard $(VENV_PYTHON_POSIX)),)
PYTHON ?= $(VENV_PYTHON_POSIX)
else
PYTHON ?= python
endif

PIP ?= $(PYTHON) -m pip
PYTEST ?= $(PYTHON) -m pytest
RUFF ?= $(PYTHON) -m ruff
CZ ?= $(PYTHON) -m commitizen
MAKE_HELPERS := $(PYTHON) scripts/make_helpers.py
BUILD ?= $(MAKE_HELPERS) build

.PHONY: help install-dev lint test build verify release clean \
	check-tools check-branch check-clean check-upstream check-release-commits

help:
	@echo "Available commands:"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make lint         - Run lint checks"
	@echo "  make test         - Run tests"
	@echo "  make build        - Build the package"
	@echo "  make verify       - Run all release checks"
	@echo "  make release      - Create a release"
	@echo "  make clean        - Remove build artifacts and caches"

install-dev:
	$(PIP) install -e .[dev]
	$(PIP) install build

lint:
	@$(RUFF) check .

test:
	@$(PYTEST) -q

build: check-tools
	@$(BUILD)

clean:
	@$(PYTHON) -c "import os, shutil; paths = ['build', 'dist', 'src/diagen.egg-info', '.pytest_cache', '.ruff_cache', '.mypy_cache', 'src/diagen/__pycache__', 'src/diagen/core/__pycache__', 'tests/__pycache__']; [shutil.rmtree(path, ignore_errors=True) for path in paths if os.path.exists(path)]"
	@echo "Build artifacts and caches removed."

verify: check-tools check-branch check-clean check-upstream check-release-commits lint test build
	@echo "All checks passed."

release: verify
	@echo "Creating the next release..."
	@$(CZ) bump --changelog --yes
	@$(BUILD)
	@echo "New version:"
	@$(CZ) version --project
	@git push --quiet $(REMOTE) HEAD
	@$(MAKE_HELPERS) push-release-tag --remote "$(REMOTE)"

check-tools:
	@$(MAKE_HELPERS) check-tools

check-branch:
	@$(MAKE_HELPERS) check-branch --allowed-branches "$(RELEASE_BRANCHES)"

check-clean:
	@$(MAKE_HELPERS) check-clean

check-upstream:
	@$(MAKE_HELPERS) check-upstream --remote "$(REMOTE)"

check-release-commits:
	@$(MAKE_HELPERS) check-release-commits

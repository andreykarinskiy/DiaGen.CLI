.PHONY: help install install-dev lint test check run version build clean changelog bump patch minor major release release-first
#

PYTHON ?= py -3.13
RELEASE_TYPE ?= auto

help:
	@echo "Доступные команды:"
	@echo "  make install      - Установить пакет"
	@echo "  make install-dev  - Установить пакет с dev-зависимостями"
	@echo "  make lint         - Запустить ruff"
	@echo "  make test         - Запустить pytest"
	@echo "  make check        - Запустить lint + test"
	@echo "  make run          - Запустить diagen"
	@echo "  make version      - Показать версию diagen"
	@echo "  make build        - Собрать wheel/sdist"
	@echo "  make clean        - Очистить артефакты сборки"
	@echo "  make changelog    - Обновить CHANGELOG через Commitizen"
	@echo "  make bump         - Интерактивный bump версии через Commitizen"
	@echo "  make patch        - Bump patch-версии"
	@echo "  make minor        - Bump minor-версии"
	@echo "  make major        - Bump major-версии"
	@echo "  make release      - SemVer release (auto|patch|minor|major) + push тегов"
	@echo "  make release-first - Создать и отправить первый тег v0.1.0"

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e .[dev]

lint:
	$(PYTHON) -m ruff check .

test:
	$(PYTHON) -m pytest -q

check: lint test

run:
	$(PYTHON) -m diagen.cli

version:
	$(PYTHON) -m diagen.cli --version

build:
	$(PYTHON) -m pip install build
	$(PYTHON) -m build

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['build', 'dist']]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').glob('*.egg-info')]"
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"

changelog:
	$(PYTHON) -m commitizen changelog

bump:
	$(PYTHON) -m commitizen bump

patch:
	$(PYTHON) -m commitizen bump --increment PATCH

minor:
	$(PYTHON) -m commitizen bump --increment MINOR

major:
	$(PYTHON) -m commitizen bump --increment MAJOR

release:
ifeq ($(RELEASE_TYPE),auto)
	$(PYTHON) -m commitizen bump --changelog
else ifeq ($(RELEASE_TYPE),patch)
	$(PYTHON) -m commitizen bump --changelog --increment PATCH
else ifeq ($(RELEASE_TYPE),minor)
	$(PYTHON) -m commitizen bump --changelog --increment MINOR
else ifeq ($(RELEASE_TYPE),major)
	$(PYTHON) -m commitizen bump --changelog --increment MAJOR
else
	$(error RELEASE_TYPE must be one of: auto, patch, minor, major)
endif
	git push origin HEAD --follow-tags

release-first:
	git tag v0.1.0
	git push origin v0.1.0

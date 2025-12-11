.PHONY: help setup install install-dev test test-cov lint format typecheck clean build

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: $(VENV)/bin/activate  ## Create virtual environment

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip

install: setup  ## Install production dependencies
	$(BIN)/pip install -r requirements.txt
	$(BIN)/pip install -e .

install-dev: setup  ## Install development dependencies
	$(BIN)/pip install -r requirements-dev.txt
	$(BIN)/pip install -e .

test: install-dev  ## Run tests
	$(BIN)/pytest

test-cov: install-dev  ## Run tests with coverage report
	$(BIN)/pytest --cov=src/glove80_visualizer --cov-report=html --cov-report=term-missing

lint: install-dev  ## Run linter and format check
	$(BIN)/ruff check src tests
	$(BIN)/ruff format --check src tests

format: install-dev  ## Format code
	$(BIN)/ruff format src tests
	$(BIN)/ruff check --fix src tests

typecheck: install-dev  ## Run type checker
	$(BIN)/mypy src

clean:  ## Clean up build artifacts and caches
	rm -rf $(VENV)
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: install-dev  ## Build distribution packages
	$(BIN)/python -m build

# Quick commands for development
run-example: install  ## Run an example visualization
	$(BIN)/glove80-viz daves-current-glove80-keymap.keymap -o output.pdf

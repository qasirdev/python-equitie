.PHONY: setup dev test lint format check build up down clean

setup:
	uv sync
	uv run pre-commit install

dev:
	uv run uvicorn backend.main:app --reload

test:
	uv run pytest backend

lint:
	uv run ruff check backend

format:
	uv run ruff format backend

check: format lint test
	uv run mypy backend

build:
	docker compose build

up:
	./scripts/start.sh

down:
	./scripts/stop.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

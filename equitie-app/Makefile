.PHONY: setup dev test lint format check build up down

setup:
	uv sync

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

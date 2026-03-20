.PHONY: dev test lint typecheck format docker-up docker-down install seed demo

install:
	uv pip install -e ".[dev,demo]"

docker-up:
	docker-compose up -d
	@echo "Waiting for PostgreSQL..."
	@sleep 3
	@echo "Services ready."

docker-down:
	docker-compose down

dev: docker-up
	uvicorn finai.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	python -m pytest tests/ -v --tb=short

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy src/finai/

seed:
	python -m demo.seed

demo:
	python -m demo.run

check: lint typecheck test

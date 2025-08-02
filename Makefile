.PHONY: help install dev-install test lint format clean build run docker-build docker-run migrate

# Default target
help:
	@echo "Clock Bucks - Available Commands:"
	@echo "  help          Show this help message"
	@echo "  install       Install production dependencies"
	@echo "  dev-install   Install development dependencies"
	@echo "  test          Run tests with coverage"
	@echo "  lint          Run linting (flake8, mypy)"
	@echo "  format        Format code (black, isort)"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build Docker image"
	@echo "  run           Run development server"
	@echo "  docker-build  Build Docker containers"
	@echo "  docker-run    Run with Docker Compose"
	@echo "  migrate       Run database migrations"

# Python environment setup
install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install

# Testing
test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-quick:
	pytest tests/ -v

# Code quality
lint:
	flake8 src tests
	mypy src

format:
	black src tests
	isort src tests

format-check:
	black --check src tests
	isort --check-only src tests

# Development
run:
	uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

run-prod:
	gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Database
migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(MSG)"

db-reset:
	rm -f clockbucks.db
	alembic upgrade head

# Docker
docker-build:
	docker build -t clockbucks-api:latest .

docker-build-prod:
	docker build -f Dockerfile.prod -t clockbucks-api:prod .

docker-run:
	docker-compose up --build

docker-run-prod:
	docker-compose -f docker-compose.prod.yml up --build

docker-down:
	docker-compose down

# Kubernetes
k8s-deploy:
	kubectl apply -f k8s/

k8s-delete:
	kubectl delete -f k8s/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Development tools
dev-setup: dev-install
	@echo "Setting up development environment..."
	pre-commit install
	@echo "Development environment ready!"

# All quality checks
check: format-check lint test

# Build and test pipeline
ci: clean install check

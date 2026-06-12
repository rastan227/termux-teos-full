.PHONY: help build up down logs migrate test lint clean backup restore seed staging prod

help:
@echo "Available commands:"
@echo "  build       Build Docker images"
@echo "  up          Start all services (development)"
@echo "  down        Stop all services"
@echo "  logs        Show logs"
@echo "  migrate     Run database migrations"
@echo "  test        Run tests"
@echo "  lint        Run linters"
@echo "  clean       Remove temporary files"
@echo "  backup      Create backup"
@echo "  restore     Restore from backup (usage: make restore FILE=path)"
@echo "  seed        Seed database with initial data"
@echo "  staging     Start staging environment"
@echo "  prod        Start production environment"

build:
docker-compose build

up:
docker-compose up -d

down:
docker-compose down

logs:
docker-compose logs -f

migrate:
docker-compose run --rm bot alembic upgrade head

test:
docker-compose run --rm bot pytest tests/ -v

lint:
docker-compose run --rm bot black --check app/
docker-compose run --rm bot flake8 app/ --max-line-length=100

clean:
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache .coverage htmlcov

backup:
./scripts/backup.sh

restore:
./scripts/restore.sh $(FILE)

seed:
docker-compose run --rm bot python scripts/seed_data.py

staging:
docker-compose -f docker-compose.staging.yml up -d

prod:
docker-compose -f docker-compose.prod.yml up -d

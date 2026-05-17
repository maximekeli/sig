.PHONY: up down build migrate seed test lint shell docs

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose exec web python manage.py migrate

seed:
	docker compose exec web python manage.py seed_demo_data

test:
	docker compose exec web pytest apps/ -v --cov=apps --cov-report=term-missing --cov-fail-under=70

test-frontend:
	cd frontend && npm install && npm test

test-all: test test-frontend

lint:
	docker compose exec web flake8 apps config --max-line-length=120

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f web

train-ml:
	docker compose exec web python manage.py train_fertility_model

ingest-nasa:
	docker compose exec web python manage.py ingest_nasa

restart:
	docker compose restart web nginx

logs-web:
	docker compose logs -f web

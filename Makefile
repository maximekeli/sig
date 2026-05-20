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
	docker compose run --rm --no-deps --entrypoint "" web pytest -q --tb=short -m "not nasa_live"

test-nasa-live:
	docker compose run --rm --no-deps --entrypoint "" -e NASA_LIVE_TESTS=1 web pytest -m nasa_live -v

test-frontend:
	cd frontend && npm test

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

rebuild-web:
	docker compose build web
	docker compose up -d --force-recreate web

logs-web:
	docker compose logs -f web

.PHONY: up down down-clean build test migrate run logs

up:
	docker-compose up --build -d

down:
	docker-compose down

down-clean:
	docker-compose down -v

build:
	docker-compose build

test:
	. .venv/bin/activate && python -m pytest tests/ -v

migrate:
	docker-compose run --rm migrations

run:
	set -a && . ./.env && set +a && \
	. .venv/bin/activate && \
	uvicorn app.server.main:app --host 0.0.0.0 --port 8000 --reload

logs:
	docker-compose logs -f app

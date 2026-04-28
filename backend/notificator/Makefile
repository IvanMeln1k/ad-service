.PHONY: up down down-clean build test run logs

## Запустить сервис (Docker)
up:
	docker-compose up --build -d

## Остановить сервис
down:
	docker-compose down

## Остановить сервис и удалить данные
down-clean:
	docker-compose down -v

## Собрать образы
build:
	docker-compose build

## Запустить юнит-тесты
test:
	. .venv/bin/activate && python -m pytest tests/ -v

## Запустить локально (без Docker)
run:
	set -a && . ./.env && set +a && \
	. .venv/bin/activate && \
	uvicorn app.server.main:app --host 0.0.0.0 --port 8000 --reload

## Логи приложения
logs:
	docker-compose logs -f app

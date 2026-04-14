.PHONY: up down build test migrate logs

## Запустить сервис (postgres + миграции + app)
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

## Применить миграции вручную
migrate:
	docker-compose run --rm migrations

## Логи приложения
logs:
	docker-compose logs -f app

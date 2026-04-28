.PHONY: up down down-clean build logs ps create-moderator create-admin

EMAIL ?= user@example.com
NAME ?= User
PASS ?= pass123

## Запустить все сервисы
up:
	docker-compose up --build -d

## Остановить все сервисы
down:
	docker-compose down

## Остановить и удалить все данные
down-clean:
	docker-compose down -v

## Собрать образы
build:
	docker-compose build

## Логи всех сервисов
logs:
	docker-compose logs -f

## Статус сервисов
ps:
	docker-compose ps

## Создать аккаунт модератора: make create-moderator EMAIL=mod@test.com NAME=Moderator PASS=pass123
create-moderator:
	./create-moderator.sh "${EMAIL}" "${NAME}" "${PASS}"

## Создать аккаунт администратора без нотификаций:
## make create-admin EMAIL=admin@test.com NAME=Admin PASS=pass123
create-admin:
	./create-admin.sh "${EMAIL}" "${NAME}" "${PASS}"

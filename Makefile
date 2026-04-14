SERVICES = backend/auther backend/profiler

.PHONY: up down down-clean

## Запустить все сервисы
up:
	@for svc in $(SERVICES); do \
		echo "Starting $$svc..."; \
		(cd $$svc && docker-compose up --build -d); \
	done

## Остановить все сервисы
down:
	@for svc in $(SERVICES); do \
		echo "Stopping $$svc..."; \
		(cd $$svc && docker-compose down); \
	done

## Остановить все сервисы и удалить данные
down-clean:
	@for svc in $(SERVICES); do \
		echo "Stopping $$svc (with volumes)..."; \
		(cd $$svc && docker-compose down -v); \
	done

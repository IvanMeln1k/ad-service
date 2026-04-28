ды.PHONY: test run

## Запустить юнит-тесты
test:
	. .venv/bin/activate && python -m pytest tests/ -v

## Запустить локально
run:
	set -a && . ./.env && set +a && \
	. .venv/bin/activate && \
	uvicorn app.server.main:app --host 0.0.0.0 --port 8000 --reload

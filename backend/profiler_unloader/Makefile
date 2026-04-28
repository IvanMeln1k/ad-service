.PHONY: test run

## Запустить юнит-тесты
test:
	. .venv/bin/activate && python -m pytest tests/ -v

## Запустить локально
run:
	set -a && . ./.env && set +a && \
	. .venv/bin/activate && \
	python -m app.main

.PHONY: help dev migrate test shell clean collectstatic createsuperuser

# Переменные
PYTHON = .\venv\Scripts\python.exe
MANAGE = $(PYTHON) manage.py

help:
	@echo "Trade Accounting - Development Commands"
	@echo ""
	@echo "make dev              - Запустить dev-сервер"
	@echo "make migrate          - Применить миграции"
	@echo "make makemigrations   - Создать миграции"
	@echo "make test             - Запустить тесты"
	@echo "make shell            - Открыть Django shell"
	@echo "make collectstatic    - Собрать статику"
	@echo "make createsuperuser  - Создать суперпользователя"
	@echo "make clean            - Очистить кеш и временные файлы"
	@echo ""
	@echo "Docker команды:"
	@echo "make docker-up        - Запустить Docker окружение"
	@echo "make docker-down      - Остановить Docker"
	@echo "make docker-logs      - Посмотреть логи"

dev:
	$(MANAGE) runserver 0.0.0.0:8000

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

test:
	$(MANAGE) test

shell:
	$(MANAGE) shell

collectstatic:
	$(MANAGE) collectstatic --noinput

createsuperuser:
	$(MANAGE) createsuperuser

clean:
	@echo "Cleaning cache and temporary files..."
	@powershell -Command "Get-ChildItem -Recurse -Filter '__pycache__' | Remove-Item -Recurse -Force"
	@powershell -Command "Get-ChildItem -Recurse -Filter '*.pyc' | Remove-Item -Force"
	@echo "Done!"

# Docker команды
docker-up:
	docker-compose -f docker-compose.local.yml up -d

docker-down:
	docker-compose -f docker-compose.local.yml down

docker-logs:
	docker-compose -f docker-compose.local.yml logs -f

docker-migrate:
	docker-compose -f docker-compose.local.yml exec web python manage.py migrate

docker-shell:
	docker-compose -f docker-compose.local.yml exec web python manage.py shell


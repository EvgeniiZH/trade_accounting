# Trade Accounting

Веб‑приложение на Django для ведения каталога товаров и расчётов с наценкой. Проект включает административный интерфейс, импорт/экспорт Excel, создание снепшотов расчётов и интеграцию с Telegram/Sentry.

## Требования

- Python 3.11
- PostgreSQL (в production), SQLite по умолчанию локально
- Redis (используется в production для кэша/сессий)
- Docker + docker-compose — для деплоя

## Локальный запуск

1. **Склонировать репозиторий**
   ```bash
   git clone https://github.com/EvgeniiZH/trade_accounting.git
   cd trade_accounting
   ```
2. **Создать виртуальное окружение**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```
3. **Установить зависимости**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Создать файл окружения**
   ```bash
   cp .env.example .env
   # Отредактировать .env: SECRET_KEY, SENTRY_DSN, TELEGRAM_* и т.д.
   ```
5. **Применить миграции и собрать статику**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
6. **Создать суперпользователя и запустить сервер**
   ```bash
   python manage.py createsuperuser
   python manage.py runserver
   ```

## Production через Docker

1. Скопировать `.env.example` в `.env.production` и заполнить переменные (Postgres, Redis, секреты, токены Telegram).
2. Запустить контейнеры:
   ```bash
   docker compose up -d --build
   docker compose exec web python manage.py migrate --noinput
   docker compose exec web python manage.py collectstatic --noinput
   ```
3. Проверить healthcheck по `http(s)://<host>/healthz`.

## Переменные окружения

| Переменная            | Назначение                                 |
|-----------------------|--------------------------------------------|
| `DJANGO_ENV`          | `local` или `production`, выбирает настройки |
| `SECRET_KEY`          | Секрет Django                              |
| `ALLOWED_HOSTS`       | Список хостов через запятую                |
| `DATABASE_* / POSTGRES_*` | Параметры БД                          |
| `SENTRY_DSN`          | DSN проекта Sentry                         |
| `TELEGRAM_BOT_TOKEN`  | Бот для уведомлений                        |
| `TELEGRAM_CHAT_ID`    | Чат/канал для уведомлений                  |
| `WEBHOOK_SECRET`      | Секрет подписи webhook’а Sentry            |

## Тесты и утилиты

```bash
python manage.py test
```

Перед пушем рекомендуется запускать `python manage.py test` и линтеры (например, `ruff`, `black`, `mypy` — можно добавить через pre-commit).

## Полезные команды

- `python manage.py createsuperuser` — создать админа
- `python manage.py dumpdata/loaddata` — экспорт/импорт данных
- `python manage.py collectstatic` — собрать статику для продакшена

## Автодеплой (GitHub Actions)

В `.github/workflows/deploy.yml` описан сценарий деплоя на VPS: после пуша в `main` репозиторий обновляется, собирается Docker‑образ, применяются миграции и статика, а затем перезагружается nginx. Следите за актуальностью `.env.production` и секретов GitHub (SSH ключ, IP сервера).

## CI/CD и Docker (единый поток)

- Разработка (локально, Docker):
  - `docker compose -f docker-compose.local.yml up`
  - Тесты внутри локала: `docker compose -f docker-compose.local.yml exec web python manage.py test -v 2`
- Staging (ветка `develop`):
  - GitHub Actions соберёт образ и задеплоит на VPS в `/opt/trade_accounting_staging` (порт 8001).
  - Требуемые секреты в GitHub → Settings → Secrets → Actions:
    - `STAGING_SSH_HOST`, `STAGING_SSH_USER`, `STAGING_SSH_KEY` (и опционально `STAGING_SSH_PORT`)
    - `GHCR_PAT` — Personal Access Token с правом `read:packages` для pull на сервере
- Production (ручной запуск workflow Release):
  - Workflow `Release (manual)` собирает образ, затем деплоит на VPS в `/opt/trade_accounting` (порт 8000) — только после ручного запуска/подтверждения.
  - Секреты: `PROD_SSH_HOST`, `PROD_SSH_USER`, `PROD_SSH_KEY` (и `PROD_SSH_PORT`), `GHCR_PAT`.

Стандартный образ: `ghcr.io/<owner>/<repo>:<tag>`. Скрипт запуска: `scripts/entrypoint.sh` (миграции/статика по флагам `MIGRATE_ON_START=1`, `COLLECTSTATIC_ON_START=1`).


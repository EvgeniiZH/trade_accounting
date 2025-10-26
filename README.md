# Trade Accounting

Система учёта торговых операций на Django.

## Требования

- Python 3.11+
- PostgreSQL (опционально, для production)
- Redis (опционально, для production)

## Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/EvgeniiZH/trade_accounting.git
cd trade_accounting
```

2. Создайте виртуальное окружение:
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/MacOS
source .venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Скопируйте `.env.example` в `.env` и настройте переменные:
```bash
cp .env.example .env
# Отредактируйте .env файл, установив необходимые значения
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер разработки:
```bash
python manage.py runserver
```

## Production Deployment

Для production используется Docker и docker-compose:

1. Настройте `.env.production`:
```bash
cp .env.example .env.production
# Отредактируйте .env.production, установив безопасные значения
```

2. Запустите сервисы:
```bash
docker-compose -f docker-compose.yml up -d
```

## Безопасность

- Никогда не коммитьте `.env` файлы
- Всегда меняйте SECRET_KEY в production
- Используйте HTTPS в production (настроено в nginx конфиге)
- Регулярно обновляйте зависимости

## Тестирование

```bash
python manage.py test
```

## Структура проекта

- `trades/` - основное приложение
  - `models.py` - модели данных
  - `views.py` - представления
  - `forms.py` - формы
  - `utils.py` - вспомогательные функции
- `templates/` - шаблоны
- `static/` - статические файлы
- `deploy/` - конфигурация для деплоя
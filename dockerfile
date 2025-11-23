# Используем более стабильный slim-образ на базе Debian 12 (bookworm)
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Устанавливаем системные зависимости с минимальным набором пакетов
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Запуск через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "trade_accounting.wsgi:application"]

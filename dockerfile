# Используем официальный образ Python (на данный момент версия 3.11)
FROM python:3.11-slim

# Устанавливаем системные зависимости (при необходимости)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код проекта в контейнер
COPY . .

# Собираем статику (если используется)
RUN python manage.py collectstatic --noinput

# Открываем порт 8000 для приложения
EXPOSE 8000

# Запускаем приложение через Gunicorn
CMD ["gunicorn", "trade_accounting.wsgi:application", "--bind", "0.0.0.0:8000"]


ENV DJANGO_SETTINGS_MODULE=trade_accounting.settings

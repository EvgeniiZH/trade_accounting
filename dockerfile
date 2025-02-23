# Используем официальный образ Python (на данный момент версия 3.11)
FROM python:3.11

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

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

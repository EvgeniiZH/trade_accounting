# Инструкция по разработке

## 🚀 Локальная разработка

### Запуск Backend (Docker)

Backend работает в Docker контейнере:

```powershell
cd C:\dev\trade_accounting
docker compose -f docker-compose.dev.yml up -d backend db
```

Backend будет доступен на: `http://localhost:8000`
API будет доступен на: `http://localhost:8000/api/`

### Запуск Frontend (локально)

Frontend запускается локально для избежания проблем с Docker volumes на Windows:

```powershell
cd C:\dev\trade_accounting\frontend
npx vite
```

Frontend будет доступен на: `http://localhost:5173`

**Важно:** Vite автоматически проксирует запросы `/api/*` на `http://localhost:8000`, поэтому API будет работать из браузера.

### Остановка

```powershell
# Остановить Docker контейнеры
docker compose -f docker-compose.dev.yml down

# Остановить Vite (Ctrl+C в терминале где он запущен)
```

## 📦 Production деплой

### Сборка и запуск на сервере

На production сервере все работает в Docker:

```bash
# Сборка и запуск всех сервисов
docker compose up -d --build

# Проверка статуса
docker compose ps

# Просмотр логов
docker compose logs -f
```

### Структура production

- **Backend (web)**: Django + Gunicorn на порту 8000 (внутренний)
- **Frontend**: Nginx на порту 80 (публичный)
- **Database (db)**: PostgreSQL
- **Redis**: для кэширования

Frontend автоматически проксирует `/api/*` запросы на backend контейнер.

### Переменные окружения

Убедитесь что файл `.env.production` содержит все необходимые переменные:
- `SECRET_KEY`
- `DEBUG=False`
- `DATABASE_URL`
- И другие настройки Django

## 🔧 Устранение проблем

### Frontend не видит файлы в Docker

Это известная проблема Docker на Windows. Решение: запускать frontend локально, как описано выше.

### Vite не запускается

Если `npx vite` не работает, попробуйте:
```powershell
cd C:\dev\trade_accounting\frontend
npm install
npx vite --host
```

### Backend не запускается

Проверьте логи:
```powershell
docker compose -f docker-compose.dev.yml logs backend
```

### Проблемы с базой данных

Пересоздайте volumes:
```powershell
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
```

# Рекомендации по улучшению безопасности

## 1. Переменные окружения

Рекомендуется добавить следующие переменные в `.env.production`:

```bash
# Django
SECRET_KEY=<сгенерированный-ключ>
WEBHOOK_SECRET=<сгенерированный-ключ-для-вебхуков>

# Database
POSTGRES_DB=trade_accounting
POSTGRES_USER=<пользователь>
POSTGRES_PASSWORD=<пароль>

# Telegram notifications
TELEGRAM_BOT_TOKEN=<токен-бота>
TELEGRAM_CHAT_ID=<id-чата>
```

## 2. Изменения в production.py

После настройки всех переменных окружения, рекомендуется обновить `production.py`:

```python
# Убрать дефолтные значения для критичных настроек
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('SECRET_KEY must be set in production')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

required_settings = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
missing_settings = [setting for setting in required_settings if not os.getenv(setting)]
if missing_settings:
    raise ImproperlyConfigured(
        f'Missing required settings: {", ".join(missing_settings)}'
    )
```

## 3. Проверка перед деплоем

1. Убедитесь, что все переменные окружения настроены
2. Сделайте бэкап базы данных
3. Протестируйте изменения локально с production настройками

## 4. Процесс обновления

1. Настройте все переменные окружения
2. Обновите `production.py`
3. Перезапустите сервисы:
```bash
docker-compose down
docker-compose up -d
```

## 5. Проверка после деплоя

1. Проверьте логи на наличие ошибок:
```bash
docker-compose logs -f web
```

2. Проверьте доступность сайта и админки
3. Проверьте работу webhook от Sentry

## 6. Откат изменений

В случае проблем:

1. Восстановите бэкап `production.py`
2. Перезапустите сервисы
```bash
docker-compose restart web
```
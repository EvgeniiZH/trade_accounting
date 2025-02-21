from .base import *
import os

DEBUG = False

# Получаем разрешённые хосты из переменной окружения (например, "example.com,www.example.com")

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '89.111.153.46,89-111-153-46.cloudvps.regruhosting.ru').split(',')
# Настройка базы данных для продакшена (например, PostgreSQL)


#При деплое используется PostgreSQL, параметры которого указываются в файле .env
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DATABASE_USER', ''),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', ''),
    }
}

# Можно добавить дополнительные настройки для продакшена, например, настройки для Whitenoise, security, logging и т.д.

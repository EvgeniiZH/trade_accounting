from .base import *
import os

DEBUG = False

# Получаем разрешённые хосты из переменной окружения (например, "example.com,www.example.com")

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '89.111.153.46,89-111-153-46.cloudvps.regruhosting.ru').split(',')
# Настройка базы данных для продакшена (например, PostgreSQL)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-3-q)1+uqx7(8i(+6zg4+r^9ed4h%&5bmc%g%nm@w2-=$89ibr-')

#При деплое используется PostgreSQL, параметры которого указываются в файле .env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'django_project_db'),
        'USER': os.getenv('POSTGRES_USER', 'django'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'me4ut9oodi3W'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Можно добавить дополнительные настройки для продакшена, например, настройки для Whitenoise, security, logging и т.д.
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
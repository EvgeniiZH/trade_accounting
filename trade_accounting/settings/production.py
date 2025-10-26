import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from django.core.exceptions import ImproperlyConfigured
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'kiteh.ru,www.kiteh.ru,89.111.153.46').split(',')

# Получаем SECRET_KEY из переменных окружения
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured(
        'SECRET_KEY must be set in production. Please check your environment variables.'
    )

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

# Проверка обязательных настроек БД
required_settings = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
missing_settings = [setting for setting in required_settings if not os.getenv(setting)]
if missing_settings:
    raise ImproperlyConfigured(
        f'The following settings must be set in production: {", ".join(missing_settings)}'
    )
STATICFILES_DIRS = [BASE_DIR / 'static']

STATIC_ROOT = '/var/www/trade_accounting/staticfiles'
MEDIA_ROOT = '/var/www/trade_accounting/media'


MEDIA_URL = '/media/'

CSRF_TRUSTED_ORIGINS = [
    "https://kiteh.ru",
    "https://www.kiteh.ru",
]

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", ""),
    integrations=[DjangoIntegration()],
    send_default_pii=True,
    traces_sample_rate=1.0,
    _experiments={"continuous_profiling_auto_start": True},
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379/1",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

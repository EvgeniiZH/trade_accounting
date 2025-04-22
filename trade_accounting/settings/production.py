import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'kiteh.ru,www.kiteh.ru,89.111.153.46').split(',')

SECRET_KEY = os.getenv('SECRET_KEY', 'замени-на-настоящий')

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

STATIC_ROOT = '/var/www/trade_accounting/staticfiles'
MEDIA_ROOT = '/var/www/trade_accounting/media'
STATICFILES_DIRS = [BASE_DIR / 'static']

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

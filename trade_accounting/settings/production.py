from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'kiteh.ru,www.kiteh.ru,89.111.153.46').split(',')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-3-q)1+uqx7(8i(+6zg4+r^9ed4h%&5bmc%g%nm@w2-=$89ibr-')

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

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


CSRF_TRUSTED_ORIGINS = [
    "https://kiteh.ru",
    "https://www.kiteh.ru",
]
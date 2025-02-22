# trade_accounting/settings/production.py
from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '89.111.153.46,example.com').split(',')
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-3-q)1+uqx7(8i(+6zg4+r^9ed4h%&5bmc%g%nm@w2-=$89ibr-')

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

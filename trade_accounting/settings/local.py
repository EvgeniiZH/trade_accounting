# trade_accounting/settings/local.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Для локальной разработки используем SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Можно явно задать секретный ключ для разработки (но не для продакшена)
SECRET_KEY = 'django-insecure-3-q)1+uqx7(8i(+6zg4+r^9ed4h%&5bmc%g%nm@w2-=$89ibr-'

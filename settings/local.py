from .base import *

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-3-q)1+uqx7(8i(+6zg4+r^9ed4h%&5bmc%g%nm@w2-=$89ibr-')

# База данных для разработки – SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

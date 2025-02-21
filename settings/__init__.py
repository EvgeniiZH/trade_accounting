# trade_accounting/settings/__init__.py
import os

# По умолчанию используем локальные настройки
env = os.environ.get('DJANGO_ENV', 'production')

if env == 'production':
    from .production import *
else:
    from .local import *

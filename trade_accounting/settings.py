import os
import dj_database_url
from pathlib import Path

# Загружаем переменные окружения
from dotenv import load_dotenv

load_dotenv()

# Определяем базовую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ Безопасность: загружаем SECRET_KEY из .env
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'замените-на-безопасный-ключ')

# ⚠️ Продакшн-режим
DEBUG = False

# 🏗 Настройка `ALLOWED_HOSTS`
ALLOWED_HOSTS = [
    'trade-accounting.onrender.com',  # Домен Render
    '127.0.0.1',
    'localhost',
]

# Добавляем Render-окружение, если оно есть
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# 🎯 Подключение к базе данных PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,  # Улучшение производительности
    )
}

# 🔐 Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌍 Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 📁 Настройки статики и медиа
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 🔒 Настройки безопасности (SSL и защита от атак)
SECURE_SSL_REDIRECT = True  # Автоматический редирект с HTTP на HTTPS
CSRF_COOKIE_SECURE = True  # CSRF-куки только через HTTPS
SESSION_COOKIE_SECURE = True  # Сессии только по HTTPS
SECURE_HSTS_SECONDS = 31536000  # HSTS на 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 📩 Email-сервер для сброса пароля и уведомлений
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_USER', 'your-email@example.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-email-password')
DEFAULT_FROM_EMAIL = 'your-email@example.com'

# 🛠 Логирование ошибок
# Проверяем, существует ли директория логов
LOG_DIR = os.getenv('LOG_DIR', BASE_DIR / 'logs')
os.makedirs(LOG_DIR, exist_ok=True)  # Создаём папку, если её нет

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

ROOT_URLCONF = 'trade_accounting.urls'

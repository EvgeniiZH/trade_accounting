#!/usr/bin/env sh
set -e

if [ "${DJANGO_WAIT_FOR_DB}" = "1" ]; then
  echo "[entrypoint] Waiting for DB ${DATABASE_HOST:-db}:${DATABASE_PORT:-5432}..."
  # Basic wait loop; replace with psql check if needed
  sleep 3
fi

if [ "${MIGRATE_ON_START}" = "1" ]; then
  echo "[entrypoint] Applying migrations..."
  python manage.py migrate --noinput
fi

if [ "${COLLECTSTATIC_ON_START}" = "1" ]; then
  echo "[entrypoint] Collecting static..."
  python manage.py collectstatic --noinput
fi

if [ "${CREATE_SUPERUSER_ON_START}" = "1" ]; then
  echo "[entrypoint] Ensuring superuser..."
  python - <<PY
import os
from django.core.management import execute_from_command_line
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE','trade_accounting.settings'))
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.getenv('DJANGO_SU_NAME','admin')
email = os.getenv('DJANGO_SU_EMAIL','admin@example.com')
password = os.getenv('DJANGO_SU_PASSWORD','admin')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('[entrypoint] Superuser created')
else:
    print('[entrypoint] Superuser exists')
PY
fi

exec "$@"
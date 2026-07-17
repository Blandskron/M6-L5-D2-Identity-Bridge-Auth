#!/usr/bin/env sh
set -e

echo "== Django entrypoint =="

# Espera opcional (por si luego pasas a Postgres)
if [ "${WAIT_FOR_STARTUP:-0}" = "1" ]; then
  echo "Waiting a bit for dependencies..."
  sleep 2
fi

# Migraciones
echo "Running migrations..."
python manage.py migrate --noinput
python manage.py setup_auth_demo

# (Opcional) makemigrations automático (NO recomendado en producción)
if [ "${DJANGO_MAKEMIGRATIONS:-0}" = "1" ]; then
  echo "Running makemigrations..."
  python manage.py makemigrations --noinput || true
  python manage.py migrate --noinput
fi

# Collectstatic (si existe STATIC_ROOT, si no, lo toleramos)
if [ "${DJANGO_COLLECTSTATIC:-1}" = "1" ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput || true
fi

# Crear superuser si vienen variables
if [ "${DJANGO_CREATE_SUPERUSER:-1}" = "1" ]; then
  echo "Ensuring superuser exists..."
  python manage.py shell << 'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin1234")

u = User.objects.filter(username=username).first()
if not u:
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created:", username)
else:
    print("Superuser already exists:", username)
PY
fi

echo "Starting server..."
exec "$@"

#!/usr/bin/env sh
set -e

echo "Aplicando migraciones..."
python manage.py migrate --noinput
python manage.py setup_auth_demo

echo "Verificando superusuario educativo..."
python manage.py shell -c "import os; from django.contrib.auth import get_user_model; U=get_user_model(); username=os.getenv('DJANGO_SUPERUSER_USERNAME','admin'); email=os.getenv('DJANGO_SUPERUSER_EMAIL','admin@example.com'); password=os.getenv('DJANGO_SUPERUSER_PASSWORD','admin1234'); user,created=U.objects.get_or_create(username=username,defaults={'email':email,'is_staff':True,'is_superuser':True}); user.is_staff=True; user.is_superuser=True; user.email=email; user.set_password(password) if created else None; user.save(); print('Superusuario creado' if created else 'Superusuario ya existente')"

python manage.py collectstatic --noinput
exec "$@"

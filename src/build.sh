#!/usr/bin/env bash
# build.sh — script de build para Render
set -o errexit

pip install -r requirements/production.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Crear superusuario si están definidas las variables de entorno
python manage.py shell -c "
import os
from apps.usuarios.models import Usuario
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
nombre = os.environ.get('DJANGO_SUPERUSER_NOMBRE', 'Admin')
if email and password:
    if not Usuario.objects.filter(email=email).exists():
        Usuario.objects.create_superuser(email=email, password=password, nombre_completo=nombre)
        print(f'Superusuario {email} creado.')
    else:
        print(f'Superusuario {email} ya existe, omitiendo.')
else:
    print('DJANGO_SUPERUSER_EMAIL / PASSWORD no configuradas, omitiendo creación.')
"

# Seed inicial si está configurado (solo corre una vez si se define la variable)
SEED_ON_BUILD="${SEED_ON_BUILD:-}"
if [ -n "$SEED_ON_BUILD" ]; then
    echo "==> Ejecutando seed_data --${SEED_ON_BUILD}"
    python manage.py seed_data --"${SEED_ON_BUILD}"
    echo "==> Seed completado. Recordá quitar SEED_ON_BUILD para deploys futuros."
fi

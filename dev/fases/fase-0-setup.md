# Fase 0 — Setup del Proyecto

> Duración estimada: 2-4 horas

## Objetivo

Proyecto Django funcional con estructura limpia, listo para desarrollar.

---

## Checklist

- [ ] Crear proyecto Django con estructura de apps separada
- [ ] Configurar settings split (base/local/production)
- [ ] Configurar PostgreSQL (o SQLite para dev rápido)
- [ ] Crear requirements.txt (base, local, production)
- [ ] Configurar .gitignore
- [ ] (Opcional) Docker + docker-compose
- [ ] (Opcional) Pre-commit hooks (black, flake8, isort)

---

## Comandos

```bash
# Crear carpeta del proyecto
mkdir planificaciones-sistema
cd planificaciones-sistema

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar Django
pip install django psycopg2-binary python-dotenv

# Crear proyecto
django-admin startproject config .

# Crear estructura de apps
mkdir apps
mkdir apps\core apps\usuarios apps\catalogos apps\instancias apps\planificaciones apps\revisiones apps\notificaciones

# Crear cada app
cd apps
python ..\manage.py startapp core core
python ..\manage.py startapp usuarios usuarios
python ..\manage.py startapp catalogos catalogos
python ..\manage.py startapp instancias instancias
python ..\manage.py startapp planificaciones planificaciones
python ..\manage.py startapp revisiones revisiones
python ..\manage.py startapp notificaciones notificaciones
cd ..
```

---

## Estructura de Settings

```python
# config/settings/base.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'django_fsm',
    'simple_history',
    # Local apps
    'apps.core',
    'apps.usuarios',
    'apps.catalogos',
    'apps.instancias',
    'apps.planificaciones',
    'apps.revisiones',
    'apps.notificaciones',
]

AUTH_USER_MODEL = 'usuarios.Usuario'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ... resto de config ...
```

```python
# config/settings/local.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

```python
# config/settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

---

## requirements/

```
# requirements/base.txt
Django>=5.0,<6.0
psycopg2-binary>=2.9
python-dotenv>=1.0
django-fsm>=2.8
django-simple-history>=3.4
python-docx>=1.1  # Para parsear Word
```

```
# requirements/local.txt
-r base.txt
django-debug-toolbar>=4.2
pytest-django>=4.7
```

---

## .env (ejemplo)

```env
SECRET_KEY=tu-secret-key-super-segura
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.local
DATABASE_URL=sqlite:///db.sqlite3
```

---

## .gitignore

```
# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Django
*.log
local_settings.py
db.sqlite3
media/

# Environment
.env
.env.*

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## Docker (opcional pero recomendado)

```dockerfile
# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/base.txt requirements/local.txt ./requirements/
RUN pip install --no-cache-dir -r requirements/local.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.9'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: planificaciones
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Verificación

```bash
# Correr migraciones iniciales
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Correr servidor
python manage.py runserver

# Visitar http://127.0.0.1:8000/admin/
```

✅ **Fase 0 completa cuando**: El admin de Django carga sin errores.

---

## Siguiente: [Fase 1 - Usuarios](fase-1-usuarios.md)

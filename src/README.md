# Sistema de Planificaciones ICES/UCSE

Sistema web para gestión de planificaciones docentes.

## Quick Start con Docker

```bash
# Copiar archivo de entorno (ya está copiado)
cp .env.example .env

# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Crear superusuario
docker-compose exec web python manage.py createsuperuser
```

El sistema estará disponible en: http://localhost:8000

## Desarrollo sin Docker

```bash
# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements/local.txt

# Configurar PostgreSQL local o cambiar a SQLite en .env
# Para SQLite temporalmente, modificar config/settings/local.py

# Migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Correr servidor
python manage.py runserver
```

## Estructura

```
src/
├── apps/                   # Django apps
│   ├── core/              # Mixins, utilidades base
│   ├── usuarios/          # Auth, roles
│   ├── catalogos/         # Carreras, materias, profesores
│   ├── instancias/        # Instancias de presentación
│   ├── planificaciones/   # Planificaciones y versiones
│   ├── revisiones/        # Flujo de aprobación
│   └── notificaciones/    # Emails
├── config/                # Configuración Django
│   ├── settings/         # Settings por entorno
│   ├── urls.py
│   └── wsgi.py
├── templates/             # Templates HTML
├── static/               # Archivos estáticos
├── media/                # Archivos subidos
└── requirements/         # Dependencias por entorno
```

## Comandos útiles

```bash
# Migraciones
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Shell Django
docker-compose exec web python manage.py shell

# Tests
docker-compose exec web pytest

# Formatear código
docker-compose exec web black .
docker-compose exec web isort .
```

## Volúmenes Docker

Los datos persisten en volúmenes Docker:
- `planificaciones_postgres_data`: Base de datos PostgreSQL
- `planificaciones_media_data`: Archivos subidos (planificaciones Word)

Para backup de la base de datos:
```bash
docker-compose exec db pg_dump -U planificaciones planificaciones > backup.sql
```

Para restaurar:
```bash
cat backup.sql | docker-compose exec -T db psql -U planificaciones planificaciones
```

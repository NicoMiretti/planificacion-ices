# Plan de Desarrollo — Sistema de Planificaciones ICES/UCSE

> Stack: **Django 5.x + Python 3.12 + PostgreSQL**

## Filosofía

1. **Vertical slices**: Cada módulo entrega funcionalidad end-to-end (modelo → vista → template).
2. **MVP primero**: Arrancar con el happy path, iterar.
3. **Tests desde el día 1**: Al menos tests de modelo y de integración básicos.
4. **Migraciones atómicas**: Una feature, una migración.

---

## Estructura del Proyecto (propuesta)

```
planificaciones/
├── manage.py
├── config/                 # Settings, URLs raíz, WSGI/ASGI
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/               # Modelos base, mixins, utils
│   ├── usuarios/           # CustomUser, roles, auth
│   ├── catalogos/          # Carrera, Materia, Profesor, Plantilla
│   ├── instancias/         # InstanciaPresentacion, audiencia
│   ├── planificaciones/    # Planificacion, Version, estados
│   ├── revisiones/         # Aprobacion, Rechazo, CorreccionLeve
│   └── notificaciones/     # Emails, templates de mail
├── templates/
├── static/
├── media/                  # Documentos Word subidos
└── tests/
```

---

## Módulos / Fases

| Fase | Módulo | Entregable | Dependencias |
|------|--------|------------|--------------|
| 0 | Setup | Proyecto Django, Docker, CI básico | — |
| 1 | Usuarios | Auth, roles (admin, moderadora, coordinador, profesor, alumno, gestion) | 0 |
| 2 | Catálogos | CRUD Carrera, Materia, Profesor, Plantillas | 1 |
| 3 | Instancias | Crear/listar instancias de presentación | 2 |
| 4 | Planificaciones (profesor) | Subir Word, validar campos, enviar, versionado | 3 |
| 5 | Revisiones | Tablero, aprobar, rechazar, doble visto | 4 |
| 6 | Consulta pública | Vista Carrera→Año→Materia, descarga oficial | 5 |
| 7 | Notificaciones | Emails (django-post_office o similar) | 3-5 |
| 8 | Reportes | Cumplimiento de plazos, exportación | 5 |
| 9 | Pulido | UX, permisos granulares, auditoría completa | 1-8 |

---

## MVP (Fases 0-5)

Objetivo: **Un profesor puede subir una planificación Word y la moderadora puede aprobarla/rechazarla.**

Ver detalle en [fases/](fases/).

---

## Decisiones Técnicas Pendientes

- [ ] ¿Validación de campos del Word server-side? (python-docx para parsear headings)
- [ ] ¿Almacenamiento de archivos: local vs S3/MinIO?
- [ ] ¿Frontend: Django templates + HTMX vs SPA (React/Vue)?
- [ ] ¿Celery para tareas async (emails, validación)?
- [ ] ¿Docker desde el día 1 o después?

**Recomendación MVP**: Django templates + HTMX para interactividad sin complejidad de SPA. Celery para emails. Docker desde el inicio para consistencia.

---

## Quick Start (después de Fase 0)

```bash
# Clonar y entrar
cd planificaciones

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements/local.txt

# Migraciones
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Correr
python manage.py runserver
```

---

## Links

- [Fase 0 - Setup](fases/fase-0-setup.md)
- [Fase 1 - Usuarios](fases/fase-1-usuarios.md)
- [Fase 2 - Catálogos](fases/fase-2-catalogos.md)
- [Fase 3 - Instancias](fases/fase-3-instancias.md)
- [Fase 4 - Planificaciones](fases/fase-4-planificaciones.md)
- [Fase 5 - Revisiones](fases/fase-5-revisiones.md)
- [Modelo de Datos](modelo-datos.md)

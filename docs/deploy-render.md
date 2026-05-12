# Deploy en Render

Esta guía asume que el repo ya está en GitHub y que tenés cuenta en [render.com](https://render.com).

---

## Qué se preparó en el código

Antes de seguir los pasos manuales, estos archivos ya están listos en el repo:

| Archivo | Qué hace |
|---|---|
| `src/build.sh` | Instala dependencias, collectstatic y migrate en cada deploy |
| `render.yaml` | Blueprint opcional (crea DB + web service en un click) |
| `src/config/settings/production.py` | Settings de producción con `DATABASE_URL` y whitenoise |
| `src/config/wsgi.py` | Default cambiado a `production` |
| `src/requirements/production.txt` | Agrega `gunicorn`, `whitenoise`, `dj-database-url` |

---

## Paso 1 — Crear la base de datos PostgreSQL

1. En el dashboard de Render: **New → PostgreSQL**
2. Completar:
   - **Name**: `planificacion-ices-db`
   - **Database**: `planificaciones`
   - **User**: `planificaciones`
   - **Region**: Oregon (o la más cercana)
   - **Plan**: Free
3. Hacer clic en **Create Database**
4. Esperar que se provisione (~1 min)
5. En la página de la DB, copiar el valor de **Internal Database URL** (lo vas a usar en el paso 2)

> ⚠️ "Internal Database URL" funciona dentro de Render. "External Database URL" es para conectarte desde tu máquina local.

---

## Paso 2 — Crear el Web Service

1. En el dashboard: **New → Web Service**
2. Conectar el repositorio de GitHub (`planificacion-ices`)
3. Completar la configuración:

| Campo | Valor |
|---|---|
| **Name** | `planificacion-ices` |
| **Region** | Oregon (mismo que la DB) |
| **Root Directory** | `src` |
| **Runtime** | Python 3 |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |
| **Plan** | Free |

> El campo **Root Directory** es importante — todo el código Django está en `src/`.

---

## Paso 3 — Variables de entorno

En la sección **Environment** del web service, agregar:

| Variable | Valor |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | Generar una clave segura (ver abajo) |
| `DEBUG` | `False` |
| `DATABASE_URL` | Pegar la **Internal Database URL** del paso 1 |
| `ALLOWED_HOSTS` | *(dejar vacío — Render inyecta `RENDER_EXTERNAL_HOSTNAME` automáticamente)* |
| `DJANGO_SUPERUSER_EMAIL` | Email del primer usuario admin (ej: `admin@ices.edu`) |
| `DJANGO_SUPERUSER_PASSWORD` | Contraseña segura para ese usuario |
| `DJANGO_SUPERUSER_NOMBRE` | Nombre completo del admin (opcional, default: `Admin`) |

> El `build.sh` crea el superusuario automáticamente al deployar si estas variables están presentes. Si el usuario ya existe, las ignora.

### Generar SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

O desde el shell de Render (después del primer deploy): **Shell → ejecutar el comando arriba**.

---

## Paso 4 — Primer deploy

1. Hacer clic en **Create Web Service**
2. Render va a clonar el repo, ejecutar `build.sh` (instala deps + collectstatic + migrate) y levantar gunicorn
3. Ver los logs en tiempo real en la pestaña **Logs**

El build debería verse así:

```
==> Running build command './build.sh'
Successfully installed Django gunicorn whitenoise ...
128 static files copied to '/app/staticfiles'
Running migrations...
  Applying planificaciones.0001_init... OK
  Applying planificaciones.0002_eliminar_estado_enviada... OK
  ...
==> Build successful
==> Starting service with 'gunicorn config.wsgi:application ...'
```

---

## Paso 5 — Seed inicial

El superusuario ya fue creado automáticamente por `build.sh` usando las variables del paso 3.

Para cargar datos iniciales, usar la opción **Shell** → **One-off Job** en Render (o esperar a que Render habilite Shell en el plan Free):

```bash
# Opción A: solo moderadora (recomendado para producción)
python manage.py seed_data --reset

# Opción B: catálogo completo (coordinadores, carreras, profesores, materias)
python manage.py seed_data --catalogo
```

> Si no tenés acceso a la Shell, también podés agregar el comando de seed al final de `build.sh` de forma temporal y hacer un deploy.

---

## Paso 6 — Verificar

- La URL del servicio queda en el dashboard (ej: `https://planificacion-ices.onrender.com`)
- Entrar con `moderadora@ices.edu` / `mod123` (si usaste `--reset` o `--catalogo`)
- Admin: `https://planificacion-ices.onrender.com/admin/`

---

## ⚠️ Limitaciones del plan Free

| Limitación | Detalle |
|---|---|
| **Sleep tras 15 min inactivo** | El servicio se "duerme". El primer request puede tardar ~30s en despertar |
| **DB PostgreSQL expira en 90 días** | Render elimina la DB gratuita a los 90 días de inactividad |
| **Sin almacenamiento persistente de media** | Los archivos subidos (planificaciones .docx) se **pierden** en cada deploy |

### Problema de media files

En el plan Free, el filesystem de Render es **efímero**: los archivos subidos después del deploy se borran en el siguiente. Para producción real hay dos opciones:

**Opción A — Render Disk (plan paid, ~$0.25/GB/mes)**

Agregar en `render.yaml`:
```yaml
disk:
  name: media
  mountPath: /app/media
  sizeGB: 1
```

**Opción B — Amazon S3 (o compatible)**

Instalar `django-storages` y `boto3`, configurar `DEFAULT_FILE_STORAGE` con un bucket S3.

Para una demo o entorno de prueba el plan Free es suficiente (los archivos se pierden pero el flujo funciona).

---

## Re-deploy automático

Render hace deploy automático en cada push a `main`. Para deshabilitar:
**Settings → Auto-Deploy → No**.

---

## Alternativa: deploy con Blueprint (render.yaml)

En lugar de los pasos manuales, podés usar el `render.yaml` que está en la raíz del repo:

1. En Render: **New → Blueprint**
2. Conectar el repo
3. Render lee `render.yaml` y crea la DB y el web service automáticamente
4. Solo tenés que agregar las variables de entorno manuales (`SECRET_KEY`, `DATABASE_URL` ya se conecta solo vía el blueprint)

> El `render.yaml` está en la raíz del repo (`planificacion-ices/render.yaml`), no en `src/`.

---

## Troubleshooting frecuente

### `ModuleNotFoundError: No module named 'config'`
El **Root Directory** no está configurado como `src`. Verificar en Settings del web service.

### `django.db.utils.OperationalError: could not connect to server`
`DATABASE_URL` no está configurada o es la URL externa en lugar de la interna. Usar la **Internal Database URL**.

### `DisallowedHost` error
Agregar el dominio de Render a `ALLOWED_HOSTS` en las variables de entorno, o verificar que `RENDER_EXTERNAL_HOSTNAME` se esté inyectando (debería ser automático).

### Static files 404
`build.sh` no corrió `collectstatic`, o `STATICFILES_STORAGE` no está configurado. Verificar que `whitenoise` esté en `MIDDLEWARE` (segundo lugar, después de `SecurityMiddleware`).

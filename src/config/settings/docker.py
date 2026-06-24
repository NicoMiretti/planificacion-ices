"""
Django settings para despliegue en Docker (contenedor propio con Postgres externo).
Hereda de base.py. Para Render usar production.py.
"""
import os
from .base import *

# ─── Core ────────────────────────────────────────────────────────────────────

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']   # obligatorio — sin default

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]

# Le indica a Django que todas sus URLs viven bajo este prefijo.
# Necesario cuando nginx hace proxy_pass con strip del prefijo (trailing slash).
FORCE_SCRIPT_NAME = os.getenv('SCRIPT_NAME', '')

# Necesario para que request.build_absolute_uri() y CSRF funcionen bien detrás del proxy
USE_X_FORWARDED_HOST = True

# Necesario para Django 4+ con proxy/dominio propio
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if o.strip()
]

# ─── Base de datos (vars individuales, Postgres externo) ─────────────────────
# Usamos getenv con defaults vacíos para que collectstatic (build-time) no falle.
# En runtime las vars siempre llegan via env_file.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.getenv('POSTGRES_DB', ''),
        'USER':     os.getenv('POSTGRES_USER', ''),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST':     os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT':     os.getenv('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# ─── Archivos estáticos (Whitenoise) ─────────────────────────────────────────

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Con FORCE_SCRIPT_NAME='/planificaciones', los templates generan URLs con el
# prefijo incluido. STATIC_URL debe tenerlo para que el browser pida la URL
# correcta (que nginx enruta a Django).
# WHITENOISE_STATIC_PREFIX='/static/' le dice a whitenoise que sus archivos
# están en '/static/...' dentro del request.path_info (ya con prefix stripeado
# por Django), independientemente de STATIC_URL.
STATIC_URL              = '/planificaciones/static/'
WHITENOISE_STATIC_PREFIX = '/static/'

# ─── Archivos de media ────────────────────────────────────────────────────────

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL  = '/planificaciones/media/'

# ─── Seguridad ────────────────────────────────────────────────────────────────

SECURE_BROWSER_XSS_FILTER      = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = 'DENY'
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True

# HSTS: habilitar solo si el contenedor está detrás de HTTPS (nginx/traefik)
SECURE_HSTS_SECONDS            = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD            = SECURE_HSTS_SECONDS > 0

# SSL redirect: desactivar si el proxy externo (nginx/traefik) ya maneja HTTPS
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() in ('true', '1', 'yes')

# Si hay proxy inverso (nginx/traefik con HTTPS), descomentar:
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ─── Email ────────────────────────────────────────────────────────────────────

EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST         = os.getenv('EMAIL_HOST', '')
EMAIL_PORT         = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER    = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD= os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS      = True
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# ─── Logging (stdout/stderr, amigable con Docker) ────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'docker': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'docker',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOG_LEVEL', 'WARNING'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

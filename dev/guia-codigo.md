# Guía de código — Sistema de Planificaciones

Para Ing. en Informática sin experiencia previa en Django/Python.
El objetivo es que puedas leer cualquier archivo del proyecto y saber exactamente qué hace y dónde tocar.

---

## 1. Cómo se estructura un proyecto Django

Un proyecto Django es básico: recibe HTTP → devuelve HTTP. El flujo siempre es el mismo:

```
Request (URL)
    → urls.py         (¿qué función maneja esta URL?)
    → views.py        (lógica: consulta DB, decide qué mostrar)
    → models.py       (acceso a la base de datos)
    → template (.html)(arma el HTML de respuesta)
Response (HTML)
```

En este proyecto hay **una carpeta por dominio** dentro de `src/apps/`:

| Carpeta | Qué contiene |
|---|---|
| `usuarios/` | El modelo de usuario, login, roles, decoradores de permisos |
| `catalogos/` | Instituciones, Carreras, Materias, Profesores, Plantillas |
| `instancias/` | Instancias de presentación (cada convocatoria de la secretaría) |
| `planificaciones/` | Planificación + Versión (FSM de estados), validador Word |
| `revisiones/` | Revision, VistoBueno, servicio de doble aprobación |
| `notificaciones/` | Envío de mails por cambios de estado |
| `core/` | Código compartido + management commands (ej: seed_data) |

---

## 2. El modelo de datos en una imagen

```
Institucion (ICES / UCSE)
  └── Carrera (Ingeniería en Sistemas, ...)
        ├── coordinador ─────────────────────── Usuario
        └── Materia (Prog I, Base de Datos, ...)
              ├── regimen: anual | 1cuat | 2cuat
              ├── anio_cursado: 1, 2, 3...
              └── profesor_titular ─────────────── Profesor ── Usuario

InstanciaPresentacion (convocatoria: "Anuales 2026")
  ├── periodo: anual | 1cuat | 2cuat
  ├── fecha_apertura / fecha_limite
  └── carreras: M2M → Carrera

Planificacion  ← una por (Materia + Profesor + Instancia)
  ├── version_oficial ──────────────────────────── Version
  └── versiones:
        Version  (v1, v2, v3 ...)
          ├── estado (FSM — ver sección 4)
          ├── archivo (.docx)
          ├── entrega_tardia / dias_atraso
          ├── campos_faltantes (JSON list)
          └── revisiones:
                Revision   (una por acción: tomar / rechazar / aprobar / correccion_leve)
                VistoBueno (uno por rol: moderadora + coordinador → doble aprobación)
```

> **Regla de oro:** `Planificacion` es el contenedor; `Version` es lo que cambia de estado.

---

## 3. El modelo de Usuario y los roles

Archivo: `src/apps/usuarios/models.py`

Django trae un `User` propio. Lo reemplazamos con uno **personalizado** que usa **email** en lugar de username y agrega el campo `rol`.

```python
class Usuario(AbstractUser):
    username = None          # eliminado, usamos email
    email = models.EmailField(unique=True)
    rol = models.CharField(choices=Rol.choices, ...)
    nombre_completo = models.CharField(...)
```

Los roles disponibles son:

| Valor en DB | Qué puede hacer |
|---|---|
| `admin` | Todo |
| `moderadora` | Crear instancias, revisar/aprobar/rechazar, corrección leve, catálogos |
| `coordinador` | Revisar/aprobar/rechazar **su** carrera |
| `profesor` | Cargar y enviar sus propias planificaciones |
| `alumno` | Solo consultar oficiales vigentes |
| `gestion` | Solo consultar oficiales vigentes |

El modelo también tiene **properties** de conveniencia, usarlas en lugar de comparar strings a mano:

```python
if request.user.es_moderadora:    # True/False
if request.user.es_revisor:       # True si es moderadora O coordinador
if request.user.puede_gestionar:  # True si es admin o moderadora
```

---

## 4. La máquina de estados (FSM) de `Version`

Archivo: `src/apps/planificaciones/models.py`

Una `Version` pasa por estos estados. **No podés saltar estados libremente**: `django-fsm` bloquea transiciones no permitidas.

```
[BORRADOR] ──enviar()──────────────────────────────► [ENVIADA]
    │                                                     │
    │ rechazar_automaticamente()                  tomar_revision()
    │ (falta campo obligatorio)                          │
    ▼                                                     ▼
[RECHAZADA_AUTO]                                  [EN_REVISION]
                                                     │       │
                                              rechazar()  aprobar() (doble visto OK)
                                                  │           │
                                                  ▼           ▼
                                            [RECHAZADA]  [APROBADA]
                                                              │
                                                       marcar_oficial()
                                                              │
                                                              ▼
                                                     [OFICIAL_VIGENTE]
                                                              │
                                                       reemplazar()
                                                       (si llega una nueva)
                                                              │
                                                              ▼
                                                       [REEMPLAZADA]
```

Para cambiar el estado de una versión **siempre usás el método de transición**, nunca asignás `version.estado = 'algo'` directamente:

```python
# ✅ Correcto
version.enviar()
version.save()

# ❌ Incorrecto — FSM lo ignorará o lanzará un error
version.estado = 'enviada'
version.save()
```

---

## 5. Control de permisos en las vistas

Archivo: `src/apps/usuarios/decorators.py`

### Qué es un decorador (`@algo`)

Un decorador es una función que **envuelve** a otra función y corre código antes (o después) de ella. La `@` es solo azúcar sintáctica de Python; estas dos formas son idénticas:

```python
# Forma con @  (la que usamos siempre)
@login_required
def mi_vista(request):
    ...

# Forma equivalente sin @  (para entender qué hace)
def mi_vista(request):
    ...
mi_vista = login_required(mi_vista)
```

Cuando llega un request a `mi_vista`, primero corre el código de `login_required`, que chequea si el usuario está autenticado. Si no lo está, redirige al login. Si sí lo está, llama a `mi_vista` normalmente.

Se pueden apilar: se ejecutan de **abajo hacia arriba** (el más cercano a la función corre primero):

```python
@login_required      # 2° — verifica login
@solo_profesor       # 1° — verifica rol (corre primero)
def cargar_planificacion(request, ...):
    ...
```

### Cómo sabe Django que el usuario está logueado

Cuando el usuario hace login, Django:
1. Verifica email + password contra la base de datos.
2. Crea una **sesión** en la tabla `django_session` (una fila con ID aleatorio + datos encriptados).
3. Le manda al navegador una **cookie** llamada `sessionid` con ese ID.

En cada request siguiente, el navegador manda la cookie automáticamente. Django la lee a través de un **middleware** (código que corre antes de llegar a cualquier vista):

```
Request entra
  → SessionMiddleware   lee la cookie sessionid → carga la sesión de la DB
  → AuthenticationMiddleware  usa la sesión → pone el usuario en request.user
  → llega a tu vista  →  request.user ya tiene el usuario autenticado (o AnonymousUser)
```

Esto está configurado en `src/config/settings/base.py` (o similar):

```python
MIDDLEWARE = [
    ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    ...
]
```

Entonces `@login_required` simplemente hace:

```python
if not request.user.is_authenticated:
    return redirect('/login/')
```

Y `request.user.is_authenticated` es `True` si el middleware encontró una sesión válida en la DB, `False` si no había cookie o la sesión expiró.

**No tenés que configurar nada**: el middleware ya está activo. Solo tenés que usar `@login_required` y Django se encarga del resto.

### Los decoradores disponibles en el proyecto

| Decorador | Viene de | Quién pasa |
|---|---|---|
| `@login_required` | Django (built-in) | Cualquier usuario autenticado |
| `@solo_moderadora` | `usuarios/decorators.py` | Solo `rol='moderadora'` (+ admin) |
| `@solo_profesor` | `usuarios/decorators.py` | Solo `rol='profesor'` |
| `@revisores` | `usuarios/decorators.py` | `rol='moderadora'` o `'coordinador'` (+ admin) |
| `@gestores` | `usuarios/decorators.py` | `rol='moderadora'` o `'admin'` |

`@login_required` es de Django y ya viene instalado. Los demás son propios del proyecto, definidos en `src/apps/usuarios/decorators.py` con `rol_requerido(...)`.

Los permisos se aplican con **decoradores** sobre las funciones de vista:

```python
from apps.usuarios.decorators import solo_profesor, revisores, gestores, solo_moderadora

@login_required          # requiere estar logueado (cualquier rol)
@solo_profesor           # solo rol='profesor'
def cargar_planificacion(request, ...):
    ...

@login_required
@revisores               # moderadora O coordinador
def tablero_revision(request):
    ...
```

Si el usuario no tiene el rol correcto, Django devuelve **403 Forbidden** automáticamente.

### Permisos a nivel de objeto (no solo de rol)

Tener el rol correcto no es suficiente en todos los casos. Hay verificaciones adicionales dentro de la vista:

```python
# El profesor solo puede enviar SU planificación
if version.planificacion.profesor != request.user.perfil_profesor:
    messages.error(request, 'No tienes permiso.')
    return redirect(...)

# El coordinador solo aprueba SU carrera
if carrera.coordinador != usuario:
    raise ValueError('No eres coordinador de esta carrera')
```

### Cómo agregar un permiso nuevo

1. Si es para un rol nuevo → agregar a `Usuario.Rol` en `models.py` y crear un decorator en `decorators.py`.
2. Si es para restringir dentro del mismo rol → agregar la verificación dentro de la vista (como los ejemplos arriba).

---

## 6. La lógica de negocio va en `services.py`

Archivo: `src/apps/revisiones/services.py`

Las **vistas** no deberían tener lógica compleja. Todo lo que sea "regla de negocio" vive en `RevisionService`:

```python
# En la vista — simple
RevisionService.aprobar(version, request.user)

# En el servicio — toda la lógica
class RevisionService:
    @staticmethod
    @transaction.atomic           # si algo falla, se revierte todo
    def aprobar(version, usuario):
        # 1. Validar estado actual
        # 2. Validar rol del usuario
        # 3. Validar que es coordinador de la carrera correcta
        # 4. Registrar VistoBueno
        # 5. Si hay doble visto → aprobar + marcar oficial
```

Cuando necesites agregar lógica nueva (ej: "cerrar instancia automáticamente"), el lugar correcto es `services.py` o un nuevo archivo de servicio, **no la vista**.

---

## 7. La validación del documento Word

Archivo: `src/apps/planificaciones/validators.py`

Cuando el profesor hace clic en "Enviar", la vista llama a `validar_documento_word(archivo)` antes de cambiar el estado. La función:

1. Abre el `.docx` con la librería `python-docx`.
2. Extrae todo el texto del documento (párrafos + tablas) en minúsculas.
3. Por cada uno de los 7 campos obligatorios, busca si alguna de sus variantes aparece en el texto.
4. Devuelve `(True, [])` si todo está o `(False, ['bibliografia', 'requisitos', ...])` si faltan campos.

```python
# Retorna una tupla: (valido: bool, faltantes: list)
es_valido, campos_faltantes = validar_documento_word(version.archivo)

if not es_valido:
    version.rechazar_automaticamente(campos_faltantes)  # FSM → RECHAZADA_AUTO
    version.save()
```

**Para agregar o cambiar un campo obligatorio**, editás la lista `CAMPOS_OBLIGATORIOS` en ese archivo:

```python
CAMPOS_OBLIGATORIOS = [
    ('proposito', ['propósito', 'proposito', 'objetivo general']),
    # agregar variante:
    ('proposito', ['propósito', 'proposito', 'objetivo general', 'meta']),
    # agregar campo nuevo:
    ('carga_horaria', ['carga horaria', 'horas semanales']),
]
```

---

## 8. El comando `seed_data` explicado paso a paso

Archivo: `src/apps/core/management/commands/seed_data.py`

Un **management command** en Django es un script Python que se corre con `python manage.py nombre_comando`. Es equivalente a un script de terminal pero con acceso completo a los modelos de Django.

El comando `seed_data` ejecuta 4 pasos en orden dentro de una **transacción atómica** (si algo falla, no queda nada a medias):

```
handle()
  ├── _flush()            → borra datos existentes (solo con --flush)
  ├── _create_users()     → crea/reutiliza los 8 usuarios de prueba
  ├── _create_catalogos() → crea instituciones, carreras, materias, profesores
  ├── _create_instancias()→ crea las instancias 2024/2025/2026
  └── _create_planificaciones() → crea planificaciones con versiones en distintos estados
```

### Por qué usa `get_or_create` en lugar de `create`

```python
# create() → falla si ya existe (error de constraint)
Institucion.objects.create(codigo='ICES', nombre='...')

# get_or_create() → busca, si no existe lo crea; devuelve (objeto, fue_creado)
ices, created = Institucion.objects.get_or_create(
    codigo='ICES',               # campo de búsqueda
    defaults={'nombre': '...'}   # campos para creación (no para búsqueda)
)
```

Así el seed puede correrse varias veces sin errores. Con `--flush` borra primero y empieza limpio.

### Cómo agregar un dato de prueba nuevo

Por ejemplo, agregar un nuevo profesor con una materia:

```python
# En _create_users(), dentro del dict:
'prof_nuevo': get_or_create('nuevo@ices.edu', 'prof123', 'profesor', 'Nombre Apellido'),

# En _create_catalogos(), al final:
prof_nuevo = get_or_create_prof(users['prof_nuevo'], ices, 'P-005')
nueva_mat  = mat('Matemática I', sistemas, 1, '1cuat', prof_nuevo)

# Agregar al dict de retorno:
return {
    ...,
    'prof_nuevo': prof_nuevo,
    'nueva_mat': nueva_mat,
}
```

---

## 9. Las funciones de ayuda en el seed

### `make_docx(*extra_lines)`
Genera un archivo `.docx` en memoria (sin escribir a disco) con los 7 campos obligatorios.
Sirve para simular documentos válidos que pasan la validación automática.

```python
# Produce un .docx con los 7 campos + un párrafo extra
contenido_bytes = make_docx('Versión 2 — revisada')
```

### `make_docx_incompleto()`
Igual pero sin bibliografía. Sirve para simular el estado `RECHAZADA_AUTO`.

### `ContentFile(contenido_bytes)`
Django trabaja con archivos como objetos de Python. `ContentFile` convierte un `bytes` en algo que Django puede guardar como si fuera un upload real:

```python
version.archivo.save('nombre.docx', ContentFile(contenido_bytes), save=False)
# save=False → guarda el archivo en disco pero NO hace .save() del modelo todavía
version.save()  # ahora sí guarda el registro en DB
```

---

## 10. Cómo correr una consulta rápida para verificar datos

Con los contenedores levantados, podés abrir un shell de Django:

```bash
docker compose exec web python manage.py shell
```

Dentro del shell (es Python interactivo):

```python
from apps.planificaciones.models import Version

# Cuántas versiones hay por estado
from django.db.models import Count
Version.objects.values('estado').annotate(n=Count('id'))

# Ver una versión específica
v = Version.objects.get(pk=1)
print(v.estado, v.entrega_tardia, v.planificacion.materia.nombre)

# Filtrar versiones enviadas
Version.objects.filter(estado='enviada').select_related('planificacion__materia')
```

---

## 11. Dónde tocar según lo que quieras hacer

| Quiero... | Archivo(s) |
|---|---|
| Agregar un campo al usuario | `usuarios/models.py` + nueva migración |
| Cambiar qué roles pueden ver una vista | `usuarios/decorators.py` o el decorador en la vista |
| Agregar un campo obligatorio al Word | `planificaciones/validators.py` → `CAMPOS_OBLIGATORIOS` |
| Cambiar la lógica de doble aprobación | `revisiones/services.py` → `RevisionService.aprobar()` |
| Agregar una transición de estado nueva | `planificaciones/models.py` → nuevo método `@transition` |
| Agregar un modelo nuevo | Nueva clase en el `models.py` de la app correspondiente + `makemigrations` |
| Agregar una URL nueva | `urls.py` de la app + función en `views.py` |
| Agregar datos de prueba | `core/management/commands/seed_data.py` |
| Ver errores del servidor | `docker compose logs web -f` |
| Acceder al admin de Django | http://localhost:8000/admin (necesitás un superuser) |

---

## 12. Flujo típico para hacer un cambio

```bash
# 1. Editar el modelo
# src/apps/catalogos/models.py → agregar campo

# 2. Crear la migración (Django detecta los cambios)
docker compose exec web python manage.py makemigrations

# 3. Aplicar la migración
docker compose exec web python manage.py migrate

# 4. Si cambia la lógica de la vista o el servicio, no hace falta migración

# 5. Verificar que no rompiste tests
docker compose exec web python manage.py test

# 6. Si querés resetear los datos de prueba
docker compose exec web python manage.py seed_data --flush
```

> **Nunca edites una migración ya aplicada.** Si cometiste un error en el modelo, creá una nueva migración que corrija.

---

## 13. Crear el superusuario para el admin

```bash
docker compose exec web python manage.py createsuperuser
# Pedirá email y password
# Luego podés ir a http://localhost:8000/admin
```

El admin de Django te da una interfaz CRUD para todos los modelos sin escribir nada. Útil para inspeccionar datos y probar permisos.

---

## 14. Ocultar un botón y bloquear la acción por URL

Son dos capas **independientes** que hay que aplicar siempre juntas. Si hacés una sola, la protección queda incompleta.

### Capa 1 — Ocultar el botón en el template

Usás `{% if %}` con `request.user.rol` o las properties del modelo. El objeto `request.user` está disponible en todos los templates:

```html
{# Solo moderadora ve este botón #}
{% if request.user.rol == 'moderadora' %}
<button class="btn btn-danger">Rechazar</button>
{% endif %}

{# O con la property del modelo (más limpio) #}
{% if request.user.es_revisor %}
<button class="btn btn-success">Aprobar</button>
{% endif %}

{# Por condición de objeto, no solo de rol #}
{% if request.user == planificacion.materia.carrera.coordinador %}
<button>Aprobar (soy coordinador de esta carrera)</button>
{% endif %}
```

Esto **solo esconde el HTML**. Si alguien conoce la URL puede ejecutar la acción igual.

### Capa 2 — Bloquear la acción en la vista (el 403)

**Caso A: el rol completo no puede acceder → usar el decorador**

```python
# views.py
from apps.usuarios.decorators import solo_moderadora

@login_required
@solo_moderadora          # cualquier otro rol → 403 automático
def rechazar_planificacion(request, version_id):
    ...
```

**Caso B: el rol puede acceder pero no a *este* objeto → verificar dentro con `PermissionDenied`**

```python
from django.core.exceptions import PermissionDenied

@login_required
@revisores   # moderadora o coordinador pasan el decorator
def aprobar(request, version_id):
    version = get_object_or_404(Version, pk=version_id)

    # Coordinador solo puede aprobar su propia carrera
    if request.user.es_coordinador:
        carrera = version.planificacion.materia.carrera
        if carrera.coordinador != request.user:
            raise PermissionDenied   # → Django devuelve 403

    # continúa la lógica...
```

`raise PermissionDenied` es el estándar de Django para devolver 403. Está importado así en todas las vistas del proyecto:

```python
from django.core.exceptions import PermissionDenied
```

### La regla

```
Template  {% if %}          →  esconde el botón (UX)
Vista     decorador / PermissionDenied  →  bloquea la acción (seguridad)
```

Siempre necesitás las dos. El template es cosmético; la vista es la protección real.

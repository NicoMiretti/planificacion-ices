# Checklist de Pruebas por Fase

Este documento describe las pruebas automatizadas y manuales para verificar cada fase del desarrollo.

---

## Comandos Generales

```bash
# Ejecutar TODOS los tests
docker-compose exec web pytest -v

# Tests de una app específica
docker-compose exec web pytest apps/usuarios/tests/ -v
docker-compose exec web pytest apps/catalogos/tests/ -v

# Tests con coverage
docker-compose exec web pytest --cov=apps --cov-report=html

# Aplicar migraciones pendientes
docker-compose exec web python manage.py migrate
```

---

## Fase 0 — Setup ✅

### Tests Automatizados
No hay tests específicos, solo verificar que el sistema levanta.

### Pruebas Manuales

| # | Prueba | Pasos | Resultado Esperado |
|---|--------|-------|-------------------|
| 0.1 | Docker levanta | `docker-compose up -d` | Contenedores `web` y `db` running |
| 0.2 | PostgreSQL conecta | Ver logs: `docker-compose logs db` | "database system is ready" |
| 0.3 | Django inicia | Ver logs: `docker-compose logs web` | "Starting development server" |
| 0.4 | Admin accesible | Navegar a http://localhost:8000/admin/ | Muestra login |

---

## Fase 1 — Usuarios ✅

### Tests Automatizados

```bash
docker-compose exec web pytest apps/usuarios/tests/ -v
```

**Tests incluidos:**
- `test_crear_usuario_con_email` — Usuario se crea con email
- `test_crear_superusuario` — Superuser tiene rol admin
- `test_email_unico` — No permite duplicados
- `test_email_obligatorio` — Email es requerido
- `test_es_admin`, `test_es_moderadora`, etc. — Helpers de rol funcionan
- `test_es_revisor` — Solo moderadora/coordinador son revisores
- `test_login_con_email` — Login funciona
- `test_login_fallido` — Credenciales inválidas fallan

### Pruebas Manuales

| # | Prueba | Pasos | Resultado Esperado |
|---|--------|-------|-------------------|
| 1.1 | Login admin | Ir a /admin/, usar admin@ices.edu / admin123 | Accede al admin |
| 1.2 | Crear usuario | Admin > Usuarios > Agregar | Usuario creado con rol seleccionado |
| 1.3 | Roles visibles | Ver usuario en admin | Muestra rol correctamente |
| 1.4 | Login frontend | Ir a /usuarios/login/ | Form de login aparece |
| 1.5 | Login exitoso | Ingresar credenciales válidas | Redirige según rol |
| 1.6 | Login fallido | Ingresar credenciales inválidas | Muestra error |
| 1.7 | Logout | Click en cerrar sesión | Vuelve al login |

### Crear Datos de Prueba

```bash
# Crear usuarios de cada rol
docker-compose exec web python manage.py shell

from apps.usuarios.models import Usuario

# Moderadora
Usuario.objects.create_user(
    email='moderadora@ices.edu',
    password='mod123',
    rol='moderadora',
    nombre_completo='Ana Moderadora'
)

# Coordinador
Usuario.objects.create_user(
    email='coordinador@ices.edu',
    password='coord123',
    rol='coordinador',
    nombre_completo='Carlos Coordinador'
)

# Profesor
Usuario.objects.create_user(
    email='profesor@ices.edu',
    password='prof123',
    rol='profesor',
    nombre_completo='María Profesora'
)

# Alumno
Usuario.objects.create_user(
    email='alumno@ices.edu',
    password='alum123',
    rol='alumno',
    nombre_completo='Pedro Alumno'
)

exit()
```

---

## Fase 2 — Catálogos ✅

### Tests Automatizados

```bash
docker-compose exec web pytest apps/catalogos/tests/ -v
```

**Tests incluidos:**
- `test_crear_institucion` — ICES/UCSE se crean
- `test_codigo_unico` — Código de institución único
- `test_crear_carrera` — Carrera con coordinador
- `test_carrera_sin_coordinador` — Carrera sin coordinador OK
- `test_nombre_unico_por_institucion` — Mismo nombre en distintas instituciones OK
- `test_crear_profesor` — Profesor vinculado a usuario
- `test_un_profesor_por_usuario` — Un usuario = un perfil profesor
- `test_crear_materia` — Materia con régimen y profesor
- `test_materia_institucion` — Hereda institución de carrera
- `test_plantilla_vigente_para` — Obtiene plantilla activa más reciente
- `test_crear_material` — MaterialApoyo se crea

### Pruebas Manuales

| # | Prueba | Pasos | Resultado Esperado |
|---|--------|-------|-------------------|
| 2.1 | Crear instituciones | Admin > Instituciones > Agregar ICES y UCSE | Aparecen en lista |
| 2.2 | Crear carrera | Admin > Carreras > Agregar | Carrera vinculada a institución |
| 2.3 | Asignar coordinador | Editar carrera, seleccionar coordinador | Solo muestra usuarios con rol coordinador |
| 2.4 | Crear profesor | Admin > Profesores > Agregar | Profesor vinculado a usuario e institución |
| 2.5 | Crear materia | Admin > Materias > Agregar | Materia con carrera, año, régimen |
| 2.6 | Asignar profesor a materia | Editar materia, seleccionar profesor | Profesor asignado |
| 2.7 | Subir plantilla | Admin > Plantillas > Agregar | Archivo subido, fecha vigente |
| 2.8 | Subir material | Admin > Materiales de apoyo > Agregar | Material con tipo y año |
| 2.9 | Filtros funcionan | Usar filtros en listas de admin | Filtra correctamente |
| 2.10 | Desactivar registro | Desmarcar "activo" en cualquier modelo | Registro inactivo |

### Crear Datos de Prueba

```bash
docker-compose exec web python manage.py shell

from apps.usuarios.models import Usuario
from apps.catalogos.models import Institucion, Carrera, Materia, Profesor
from datetime import date

# Instituciones
ices = Institucion.objects.create(
    nombre='Instituto de Ciencias y Estudios Superiores',
    codigo='ICES'
)
ucse = Institucion.objects.create(
    nombre='Universidad Católica de Santiago del Estero',
    codigo='UCSE'
)

# Coordinador (debe existir de Fase 1)
coord = Usuario.objects.get(email='coordinador@ices.edu')

# Carrera
sistemas = Carrera.objects.create(
    nombre='Ingeniería en Sistemas',
    institucion=ices,
    coordinador=coord
)

# Profesor (necesita usuario profesor de Fase 1)
usuario_prof = Usuario.objects.get(email='profesor@ices.edu')
prof = Profesor.objects.create(
    usuario=usuario_prof,
    institucion=ices,
    legajo='12345'
)

# Materias
Materia.objects.create(
    nombre='Programación I',
    carrera=sistemas,
    anio_cursado=1,
    regimen='anual',
    profesor_titular=prof
)
Materia.objects.create(
    nombre='Base de Datos',
    carrera=sistemas,
    anio_cursado=2,
    regimen='1cuat',
    profesor_titular=prof
)
Materia.objects.create(
    nombre='Sistemas Operativos',
    carrera=sistemas,
    anio_cursado=3,
    regimen='anual'
)

print("Datos de prueba creados!")
exit()
```

---

## Fase 3 — Instancias (pendiente)

### Tests a implementar
- Crear instancia de presentación
- Audiencia (carreras, régimen)
- Estados: programada → abierta → cerrada
- Calcular materias de la audiencia
- Consultar instancias por profesor

### Pruebas Manuales Esperadas
| # | Prueba | CU Relacionado |
|---|--------|----------------|
| 3.1 | Crear instancia con fecha futura | CU-01 |
| 3.2 | Instancia se abre automáticamente | CU-01 |
| 3.3 | Seleccionar audiencia (carreras) | CU-01 |
| 3.4 | Profesor ve sus instancias | CU-06 |
| 3.5 | Histórico de instancias pasadas | CU-06 |

---

## Fase 4 — Planificaciones (pendiente)

### Tests a implementar
- Subir documento Word
- Validación de campos obligatorios
- Rechazo automático si falta campo
- Versionado correlativo
- Marca de entrega tardía

### Pruebas Manuales Esperadas
| # | Prueba | CU Relacionado |
|---|--------|----------------|
| 4.1 | Profesor sube Word | CU-07 |
| 4.2 | Enviar → validación campos | CU-08 |
| 4.3 | Rechazo automático | CU-08 |
| 4.4 | Envío exitoso → versión creada | CU-08 |
| 4.5 | Entrega tardía marcada | CU-08 |
| 4.6 | Ver historial de versiones | CU-09 |
| 4.7 | Clonar planificación anterior | CU-14 |

---

## Fase 5 — Revisiones (pendiente)

### Tests a implementar
- Tomar planificación para revisión
- Aprobar (visto bueno individual)
- Doble aprobación → oficial
- Rechazar con observaciones
- Corrección leve

### Pruebas Manuales Esperadas
| # | Prueba | CU Relacionado |
|---|--------|----------------|
| 5.1 | Tablero muestra pendientes | CU-02 |
| 5.2 | Filtros del tablero | CU-02 |
| 5.3 | Coordinador ve solo su carrera | CU-02 |
| 5.4 | Dar visto bueno | CU-03 |
| 5.5 | Doble visto → aprobada | CU-03 |
| 5.6 | Rechazar con texto | CU-04 |
| 5.7 | Corrección leve (moderadora) | CU-05 |
| 5.8 | Profesor notificado | CU-03, CU-04 |

---

## Resumen de Cobertura

| Fase | Tests Auto | Pruebas Manuales | Estado |
|------|------------|------------------|--------|
| 0 - Setup | — | 4 | ✅ |
| 1 - Usuarios | 10 | 7 | ✅ |
| 2 - Catálogos | 15 | 10 | ✅ |
| 3 - Instancias | — | — | Pendiente |
| 4 - Planificaciones | — | — | Pendiente |
| 5 - Revisiones | — | — | Pendiente |

---

## Después de Cada Fase

1. ✅ Ejecutar tests automatizados
2. ✅ Ejecutar pruebas manuales del checklist
3. ✅ Crear datos de prueba para la siguiente fase
4. ✅ Commit con mensaje descriptivo

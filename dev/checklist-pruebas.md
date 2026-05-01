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

## Fase 3 — Instancias ✅

### Tests Automatizados

```bash
docker-compose exec web pytest apps/instancias/tests/ -v
```

**Tests incluidos:**
- `test_crear_instancia_basica` — Instancia con fechas y período
- `test_estado_programada_antes_apertura` — Estado según fechas
- `test_estado_abierta_entre_fechas` / `test_estado_abierta_despues_limite` — Apertura y tardías
- `test_cerrada_manual_no_reabre` — Cierre manual definitivo
- `test_materias_audiencia_por_carrera` / filtro regímen / filtro institución
- `test_profesores_audiencia` — Profesores de la audiencia
- `test_manager_activas` / `test_manager_abiertas` / `test_manager_para_profesor`
- `test_lista_instancias_requiere_moderadora` / `test_mis_instancias_profesor` / `test_detalle_instancia`

### Pruebas Manuales

| # | Prueba | Pasos | Resultado Esperado |
|---|--------|-------|-------------------|
| 3.1 | Crear instancia | Admin > Instancias > Agregar | Instancia con estado `programada` |
| 3.2 | Instancia se abre | Fijar fecha apertura = hoy, reiniciar | Estado cambia a `abierta` |
| 3.3 | Seleccionar carreras | Editar instancia, agregar carreras | Solo esas carreras en audiencia |
| 3.4 | Profesor ve instancias | Login como profesor → /instancias/mis/ | Solo instancias con sus materias |
| 3.5 | Detalle instancia | Click en instancia | Muestra materias y botón cargar |

---

## Fase 4 — Planificaciones ✅

### Tests Automatizados

```bash
docker-compose exec web pytest apps/planificaciones/tests/ -v
```

**Tests incluidos:**
- `test_documento_completo_es_valido` / `test_documento_incompleto_no_es_valido` / `test_documento_vacio_falla`
- `test_nombre_campo_devuelve_string` / `test_variantes_de_campo`
- `test_crear_planificacion` / `test_unique_together`
- `test_siguiente_numero_version_sin_versiones` / `test_siguiente_numero_version_con_versiones`
- `test_estado_inicial_borrador` / `test_enviar_cambia_estado` / `test_rechazar_automaticamente`
- `test_flujo_completo_aprobacion` / `test_flujo_rechazo_revisor`
- `test_entrega_en_plazo` / `test_entrega_tardia`
- `test_cargar_requiere_login` / `test_profesor_accede_a_cargar` / `test_subir_archivo_crea_version`
- `test_enviar_version_valida` / `test_enviar_version_invalida_rechaza_auto`

### Pruebas Manuales

| # | Prueba | Pasos | Resultado Esperado |
|---|--------|-------|-------------------|
| 4.1 | Profesor sube Word | Instancia > materia > Cargar planificación | Borrador v1 creado |
| 4.2 | Enviar doc completo | Detalle planificación > Enviar | Estado `enviada` |
| 4.3 | Rechazo automático | Enviar doc sin campos | Estado `rechazada_auto` + lista de campos faltantes con nombres legibles |
| 4.4 | Segunda versión | Subir nuevo archivo | Se crea v2 |
| 4.5 | Entrega tardía | Instancia fuera de plazo, enviar | Marca tardía + días de atraso |
| 4.6 | Descargar versión | Click en ↓ Descargar | Descarga el .docx |
| 4.7 | Clonar planificación | Link clonar en cargar | Copia archivo oficial previo como borrador |

### Crear Datos de Prueba (Fase 4)

```bash
docker-compose exec web python manage.py shell

from apps.instancias.models import InstanciaPresentacion
from apps.catalogos.models import Carrera
from datetime import date, timedelta

sistemas = Carrera.objects.get(nombre='Ingeniía en Sistemas')

instancia = InstanciaPresentacion.objects.create(
    nombre='Planificaciones 2026',
    anio_academico=2026,
    periodo='anual',
    fecha_apertura=date.today() - timedelta(days=5),
    fecha_limite=date.today() + timedelta(days=25),
)
instancia.carreras.add(sistemas)
print(f'Instancia creada: {instancia} (estado: {instancia.estado})')
exit()
```

---

## Fase 5 — Revisiones ✅

### Tests Automatizados

```bash
docker-compose exec web pytest apps/revisiones/tests/ -v
```

**Tests incluidos:**
- `test_tomar_cambia_estado` / `test_tomar_crea_registro_revision` / `test_no_se_puede_tomar_borrador`
- `test_primer_visto_no_aprueba` / `test_doble_visto_aprueba_y_marca_oficial`
- `test_no_se_puede_aprobar_dos_veces_mismo_rol` / `test_coordinador_incorrecto_no_puede_aprobar` / `test_profesor_no_puede_aprobar`
- `test_rechazar_cambia_estado` / `test_rechazar_crea_revision_con_observaciones`
- `test_rechazar_sin_observaciones_falla` / `test_rechazar_observaciones_solo_espacios_falla`
- `test_moderadora_puede_corregir` / `test_corrección_no_cambia_estado`
- `test_coordinador_no_puede_corregir` / `test_corrección_sin_detalle_falla`
- `test_tablero_requiere_login` / `test_tablero_requiere_rol_revisor`
- `test_tablero_accesible_moderadora` / `test_tablero_accesible_coordinador`
- `test_aprobar_via_post` / `test_rechazar_via_post` / `test_rechazar_sin_observaciones_no_cambia_estado`

### Pruebas Manuales

| # | Prueba | Pasos | Resultado Esperado |
|---|--------|-------|-------------------|
| 5.1 | Tablero muestra pendientes | Login moderadora → /revisiones/ | Lista versiones enviadas/en revisión |
| 5.2 | Filtro por carrera | Usar filtro carrera en tablero | Solo muestra esa carrera |
| 5.3 | Coordinador ve solo su carrera | Login coordinador → tablero | Solo ve materias de su carrera |
| 5.4 | Dar visto bueno | Revisar > Dar Visto Bueno | Badge verde en sección aprobación |
| 5.5 | Doble visto → oficial | Moderadora + coordinador aprueban | Estado cambia a Oficial |
| 5.6 | Rechazar con texto | Revisar > Rechazar + observaciones | Estado `rechazada`, texto guardado |
| 5.7 | Rechazar sin texto | Intentar rechazar sin observaciones | Error, estado no cambia |
| 5.8 | Corrección leve (moderadora) | Revisar > Corrección Leve | Registro guardado, estado sigue en revisión |

---

## Resumen de Cobertura

| Fase | Tests Auto | Pruebas Manuales | Estado |
|------|------------|------------------|---------|
| 0 - Setup | — | 4 | ✅ |
| 1 - Usuarios | 13 | 7 | ✅ |
| 2 - Catálogos | 18 | 10 | ✅ |
| 3 - Instancias | 17 | 5 | ✅ |
| 4 - Planificaciones | 24 | 7 | ✅ |
| 5 - Revisiones | 23 | 8 | ✅ |

**Total tests automáticos: 95**

---

## Después de Cada Fase

1. ✅ Ejecutar tests automatizados
2. ✅ Ejecutar pruebas manuales del checklist
3. ✅ Crear datos de prueba para la siguiente fase
4. ✅ Commit con mensaje descriptivo

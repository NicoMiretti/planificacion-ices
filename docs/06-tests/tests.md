# Tests del Sistema

> Documentación de las pruebas automatizadas del sistema de planificaciones.

## Ejecutar Tests

```bash
# Todos los tests
docker-compose exec web pytest -v

# Tests con cobertura
docker-compose exec web pytest --cov=apps --cov-report=html

# Tests de una app específica
docker-compose exec web pytest apps/usuarios/tests/ -v
docker-compose exec web pytest apps/catalogos/tests/ -v
docker-compose exec web pytest apps/instancias/tests/ -v
docker-compose exec web pytest apps/planificaciones/tests/ -v

# Un test específico
docker-compose exec web pytest apps/usuarios/tests/test_usuarios.py::TestUsuarioModel::test_crear_usuario_con_email -v
```

---

## Tests por Módulo

### 1. Usuarios (`apps/usuarios/tests/`)

Relacionado con: [CU-16 Gestionar catálogos](04-casos-de-uso/casos-de-uso.md#cu-16--gestionar-catálogos) (parte de usuarios)

#### TestUsuarioModel

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_crear_usuario_con_email` | Crea usuario con email como identificador único | RNF-002 |
| `test_crear_superusuario` | Superuser se crea con rol admin y permisos completos | RNF-003 |
| `test_email_unico` | No permite crear dos usuarios con el mismo email | RNF-002 |
| `test_email_obligatorio` | El email es campo requerido | RNF-002 |

#### TestUsuarioRoles

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_es_admin` | Helper `es_admin` identifica correctamente administradores | RNF-003 |
| `test_es_moderadora` | Helper `es_moderadora` identifica a la secretaría académica | RNF-003 |
| `test_es_coordinador` | Helper `es_coordinador` identifica coordinadores de carrera | RNF-003 |
| `test_es_profesor` | Helper `es_profesor` identifica profesores titulares | RNF-003 |
| `test_es_revisor` | Solo moderadora y coordinador pueden revisar planificaciones | RN-03 |
| `test_es_consulta` | Alumno y gestión solo tienen acceso de consulta | RF-051, RF-052 |
| `test_puede_gestionar` | Solo admin y moderadora pueden gestionar catálogos | RF-001 a RF-004 |

#### TestUsuarioAuth

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_login_con_email` | Autenticación exitosa con email y contraseña válidos | RNF-002 |
| `test_login_fallido` | Credenciales inválidas no permiten acceso | RNF-002 |

---

### 2. Catálogos (`apps/catalogos/tests/`)

Relacionado con: [CU-16 Gestionar catálogos](04-casos-de-uso/casos-de-uso.md#cu-16--gestionar-catálogos)

#### TestInstitucion

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_crear_institucion` | Crea institución con código único (ICES/UCSE) | RF-003 |
| `test_codigo_unico` | No permite códigos de institución duplicados | RF-003 |

#### TestCarrera

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_crear_carrera` | Crea carrera vinculada a institución y coordinador | RF-001 |
| `test_carrera_str` | Representación string incluye nombre e institución | — |
| `test_carrera_sin_coordinador` | Carrera puede existir sin coordinador asignado | RF-001 |
| `test_nombre_unico_por_institucion` | Mismo nombre permitido en distintas instituciones | RF-001 |

#### TestProfesor

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_crear_profesor` | Crea perfil de profesor vinculado a usuario | RF-002 |
| `test_profesor_str` | Representación string muestra nombre completo | — |
| `test_un_profesor_por_usuario` | Un usuario solo puede tener un perfil de profesor | RN-09 |

#### TestMateria

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_crear_materia` | Crea materia con carrera, año, régimen y profesor | RF-001 |
| `test_materia_str` | Representación string muestra nombre, carrera y año | — |
| `test_materia_institucion` | Materia hereda institución de la carrera | RF-003 |
| `test_regimenes_validos` | Valida régimenes: anual, 1°cuat, 2°cuat | RN-05 |
| `test_materia_sin_profesor` | Materia puede existir sin profesor asignado | RF-001 |

#### TestPlantilla

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_plantilla_vigente_para` | Obtiene la plantilla activa más reciente por institución | RF-004, RF-021 |
| `test_plantilla_inactiva_no_vigente` | Plantillas inactivas no se consideran vigentes | RF-004 |

#### TestMaterialApoyo

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_crear_material` | Crea material de apoyo con tipo y año académico | RF-004 |
| `test_tipos_validos` | Valida tipos: reglamento, calendario, guía APA, etc. | RF-012 |

---

### 3. Instancias (`apps/instancias/tests/`)

Relacionado con: [CU-01 Crear instancia de presentación](04-casos-de-uso/casos-de-uso.md#cu-01), [CU-06 Ver instancias asignadas](04-casos-de-uso/casos-de-uso.md#cu-06)

#### TestInstanciaPresentacionModelo

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_crear_instancia_basica` | Crea instancia con nombre, año, período y fechas | CU-01 |
| `test_estado_programada_antes_apertura` | Estado es `programada` si hoy es antes de fecha_apertura | RN-01 |
| `test_estado_abierta_entre_fechas` | Estado es `abierta` entre apertura y límite | RN-01 |
| `test_estado_abierta_despues_limite` | Estado sigue `abierta` após fecha_límite (acepta tardías) | RN-08 |
| `test_cerrada_manual_no_reabre` | Una instancia cerrada manualmente no cambia de estado | RN-01 |

#### TestInstanciaAudiencia

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_materias_audiencia_por_carrera` | `materias_audiencia()` devuelve materias de las carreras configuradas | CU-01, CU-06 |
| `test_materias_audiencia_filtro_regimen` | Filtro por régimen excluye materias de otro régimen | CU-01 |
| `test_materias_audiencia_filtro_institucion` | Filtro por institución excluye materias de otra institución | CU-01 |
| `test_profesores_audiencia` | `profesores_audiencia()` devuelve profesores con materias en la audiencia | CU-06 |

#### TestInstanciaManager

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_manager_activas` | `.activas()` devuelve solo instancias programadas y abiertas | CU-06 |
| `test_manager_abiertas` | `.abiertas()` devuelve solo instancias con estado abierta | CU-06 |
| `test_manager_para_profesor` | `.para_profesor(usuario)` devuelve instancias con materias del profesor | CU-06 |
| `test_manager_para_profesor_sin_perfil` | `.para_profesor()` con usuario sin perfil devuelve queryset vacío | CU-06 |

#### TestInstanciaViews

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_lista_instancias_requiere_moderadora` | Vista `lista` redirige si el usuario no es moderadora | CU-01 |
| `test_lista_instancias_moderadora_accede` | Moderadora accede correctamente a la lista de instancias | CU-01 |
| `test_mis_instancias_profesor` | Profesor ve sus instancias activas en `/instancias/mis/` | CU-06 |
| `test_detalle_instancia` | Detalle muestra las materias de la audiencia | CU-01, CU-06 |

---

## Tests Pendientes (por fase)

### Fase 4 — Planificaciones

---

### 4. Planificaciones (`apps/planificaciones/tests/`)

Relacionado con: [CU-07 Cargar planificación](04-casos-de-uso/casos-de-uso.md#cu-07), [CU-08 Enviar planificación](04-casos-de-uso/casos-de-uso.md#cu-08), [CU-14 Clonar planificación](04-casos-de-uso/casos-de-uso.md#cu-14)

#### TestValidador (sin DB)

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_documento_completo_es_valido` | Documento con los 7 campos pasa la validación | RN-06 |
| `test_documento_incompleto_no_es_valido` | Documento con campos faltantes falla y lista los faltantes | RN-06 |
| `test_documento_vacio_falla` | Documento vacío falla con los 7 campos faltantes | RN-06 |
| `test_nombre_campo_devuelve_string` | `nombre_campo()` retorna texto legible para el usuario | — |
| `test_variantes_de_campo` | Acepta variantes textuales del mismo campo (sin tilde, sinónimos) | RN-06 |

#### TestPlanificacionModelo

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_crear_planificacion` | Crea planificación para materia/profesor/instancia | CU-07 |
| `test_unique_together` | No permite duplicar planificación para la misma combinación | RN-09 |
| `test_siguiente_numero_version_sin_versiones` | Sin versiones, el siguiente número es 1 | RF-025 |
| `test_siguiente_numero_version_con_versiones` | Con versiones existentes, incrementa correctamente | RF-025 |
| `test_no_tiene_oficial_inicialmente` | Nueva planificación no tiene versión oficial | — |
| `test_ultima_version_none_sin_versiones` | Sin versiones, `ultima_version` devuelve None | — |

#### TestVersionFSM

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_estado_inicial_borrador` | Una versión nueva empieza en estado `borrador` | CU-07 |
| `test_enviar_cambia_estado` | `enviar()` cambia estado a `enviada` y registra fecha | CU-08 |
| `test_rechazar_automaticamente` | `rechazar_automaticamente()` cambia a `rechazada_auto` y guarda campos faltantes | CU-08, RN-06 |
| `test_flujo_completo_aprobacion` | Flujo: borrador → enviada → en_revisión → aprobada | CU-02, CU-03 |
| `test_flujo_rechazo_revisor` | Flujo: borrador → enviada → en_revisión → rechazada | CU-04 |

#### TestEntregaTardia

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_entrega_en_plazo` | Entrega dentro del plazo no se marca como tardía | RN-08 |
| `test_entrega_tardia` | Entrega fuera del plazo se marca como tardía con días de atraso | RN-08 |

#### TestPlanificacionViews

| Test | Descripción | Regla/RF |
|------|-------------|----------|
| `test_cargar_requiere_login` | Vista `cargar` redirige si no está autenticado | — |
| `test_detalle_requiere_login` | Vista `detalle` redirige si no está autenticado | — |
| `test_profesor_accede_a_cargar` | Profesor titular puede ver el formulario de carga | CU-07 |
| `test_subir_archivo_crea_version` | POST con archivo Word crea un borrador v1 | CU-07 |
| `test_enviar_version_valida` | Enviar doc con 7 campos → estado `enviada` | CU-08 |
| `test_enviar_version_invalida_rechaza_auto` | Enviar doc incompleto → estado `rechazada_auto` con campos faltantes | CU-08, RN-06 |

---

## Tests Pendientes (por fase)

### Fase 5 — Revisiones

| Test Esperado | CU Relacionado |
|---------------|----------------|
| `test_tomar_para_revision` | CU-02 |
| `test_aprobar_visto_bueno` | CU-03 |
| `test_doble_aprobacion_oficial` | CU-03, RN-03 |
| `test_rechazar_con_observaciones` | CU-04 |
| `test_rechazo_requiere_texto` | CU-04 |
| `test_correccion_leve` | CU-05, RN-07 |
| `test_solo_moderadora_corrige` | CU-05 |
| `test_coordinador_ve_su_carrera` | CU-02, RF-031 |

---

## Cobertura Actual

| Módulo | Tests | Estado |
|--------|-------|--------|
| usuarios | 13 | ✅ Completo |
| catalogos | 18 | ✅ Completo |
| instancias | 17 | ✅ Completo |
| planificaciones | 24 | ✅ Completo |
| revisiones | 0 | ⏳ Fase 5 |
| notificaciones | 0 | ⏳ Fase 7 |

**Total actual: 72 tests**

---

## Convenciones

### Estructura de Tests

```python
@pytest.mark.django_db
class TestNombreModelo:
    """Tests del modelo NombreModelo."""

    def test_crear_modelo(self):
        """Descripción clara de qué verifica."""
        # Arrange
        dato = crear_dato()
        
        # Act
        resultado = operacion(dato)
        
        # Assert
        assert resultado.campo == valor_esperado
```

### Fixtures

- Definir fixtures en el mismo archivo o en `conftest.py`
- Usar nombres descriptivos: `institucion_ices`, `usuario_profesor`
- Marcar con `@pytest.fixture`

### Naming

- Archivos: `test_<modulo>.py`
- Clases: `Test<Modelo>` o `Test<Funcionalidad>`
- Métodos: `test_<accion>_<resultado_esperado>`

---

## Referencias

- [Requerimientos](03-requerimientos/requerimientos.md)
- [Casos de Uso](04-casos-de-uso/casos-de-uso.md)
- [Checklist de Pruebas](../dev/checklist-pruebas.md)

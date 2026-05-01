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

## Tests Pendientes (por fase)

### Fase 3 — Instancias

| Test Esperado | CU Relacionado |
|---------------|----------------|
| `test_crear_instancia` | CU-01 |
| `test_instancia_audiencia_carreras` | CU-01 |
| `test_instancia_fechas_validacion` | CU-01 |
| `test_instancia_estado_programada` | CU-01 |
| `test_instancia_estado_abierta` | CU-01 |
| `test_materias_audiencia` | CU-01, CU-06 |
| `test_profesores_audiencia` | CU-01, CU-06 |
| `test_instancias_para_profesor` | CU-06 |

### Fase 4 — Planificaciones

| Test Esperado | CU Relacionado |
|---------------|----------------|
| `test_crear_planificacion` | CU-07 |
| `test_subir_archivo_word` | CU-07 |
| `test_validar_campos_obligatorios` | CU-08, RN-06 |
| `test_rechazo_automatico_campo_faltante` | CU-08, RN-06 |
| `test_envio_exitoso` | CU-08 |
| `test_versionado_correlativo` | CU-08, RF-025 |
| `test_marca_entrega_tardia` | CU-08, RN-08 |
| `test_clonar_oficial_previa` | CU-14, RF-026 |

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
| instancias | 0 | ⏳ Fase 3 |
| planificaciones | 0 | ⏳ Fase 4 |
| revisiones | 0 | ⏳ Fase 5 |
| notificaciones | 0 | ⏳ Fase 7 |

**Total actual: 31 tests**

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

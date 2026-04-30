# Requerimientos

> Origen principal: [acta-2026-04-30-moderadora.md](../02-relevamiento/actas/acta-2026-04-30-moderadora.md).

## Funcionales

### Gestión de catálogos
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-001 | Cargar el listado anual de **carreras** y, para cada una, sus **materias** con régimen (anual / 1° cuat / 2° cuat) y **año de cursado**. | Alta |
| RF-002 | Asignar un **profesor titular** a cada materia. | Alta |
| RF-003 | Asociar cada profesor a una **institución** (ICES o UCSE) para notificación y plantilla. | Alta |
| RF-004 | Mantener las **plantillas** vigentes (ICES y UCSE) y los **materiales de apoyo** (reglamento, calendario, guía APA, doc orientador). | Alta |

### Instancias de presentación
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-010 | Crear **instancias de presentación** programables: período cubierto, audiencia (carrera/s, institución, materias), fecha de apertura, fecha límite. | Alta |
| RF-011 | Disparar **notificación por mail** a los profesores de la audiencia al abrir la instancia, en grupos por institución. | Alta |
| RF-012 | El mail incluirá link a los materiales de apoyo y al sistema. | Alta |
| RF-013 | Soportar **múltiples instancias** activas en paralelo (ej. anuales + cuatrimestrales). | Alta |
| RF-014 | Recordatorios automáticos al profesor antes de la fecha límite (configurable). | Media |

### Carga y envío (profesor)
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-020 | El profesor verá la lista de instancias en las que debe presentar. | Alta |
| RF-021 | El profesor completará la planificación según la **plantilla** correspondiente a su institución. | Alta |
| RF-022 | El sistema **validará automáticamente** la presencia de los 7 campos obligatorios (ver [estructura-planificacion.md](../01-vision/estructura-planificacion.md)). | Alta |
| RF-023 | Si falta un campo obligatorio, el sistema **rechazará automáticamente** el envío indicando qué falta. | Alta |
| RF-024 | El profesor podrá enviar la planificación al circuito de revisión. | Alta |
| RF-025 | El sistema asignará un **número de versión** correlativo por (profesor, materia, período). | Alta |
| RF-026 | El profesor podrá **clonar** una planificación oficial previa como punto de partida. | Media |
| RF-027 | Si la entrega ocurre **después de la fecha límite**, el sistema marcará la versión como **entrega tardía** sin bloquear el envío. | Alta |
| RF-028 | El sistema mostrará al profesor el estado actual y las observaciones recibidas. | Alta |

### Revisión (moderadora + coordinador)
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-030 | La moderadora verá un **tablero** de planificaciones recibidas, filtrable por carrera, año, materia, estado, institución, instancia. | Alta |
| RF-031 | El coordinador verá el subconjunto correspondiente a su carrera/área. | Alta |
| RF-032 | La aprobación final requiere **doble visto** (moderadora + coordinador correspondiente). | Alta |
| RF-033 | Moderadora y coordinador podrán **rechazar** dejando observaciones (texto libre). | Alta |
| RF-034 | La moderadora podrá registrar **correcciones leves** propias sin devolver al profesor; quedan asentadas en el histórico. | Media |
| RF-035 | Moderadora + coordinador podrán **dar por cerrado** un ciclo de revisión (definir y aprobar) si las idas y vueltas se prolongan. | Media |

### Versión oficial e histórico
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-040 | Al lograr la doble aprobación, el sistema marcará la versión como **oficial vigente** del período. | Alta |
| RF-041 | Solo puede existir **una** versión oficial vigente por (profesor, materia, período). | Alta |
| RF-042 | Permitir **modificar una planificación ya aprobada**: la nueva pasa a vigente; la anterior queda en histórico identificable. | Alta |
| RF-043 | El histórico conservará todas las versiones (enviadas, rechazadas, aprobadas, reemplazadas) con autor, fecha, observaciones y motivo. | Alta |

### Consulta
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-050 | **Pantalla principal** organizada por **Carrera → Año de cursado → Materia**, mostrando estado y oficial vigente. | Alta |
| RF-051 | El **alumnado** podrá consultar la versión oficial vigente de cada materia. | Alta |
| RF-052 | **Secretarías generales / equipo de gestión** podrán consultar y descargar oficiales. | Alta |
| RF-053 | El **histórico de rechazos** será visible solo para moderadora y coordinador correspondiente. | Alta |
| RF-054 | Reporte de **cumplimiento de plazos** por profesor/materia/instancia (insumo para el premio por objetivos). | Media |

### Notificaciones
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-060 | Notificar por **mail a la secretaría** cuando llega una planificación nueva. | Alta |
| RF-061 | Notificar al profesor los cambios de estado (rechazo con observaciones, aprobación, corrección leve aplicada). | Alta |
| RF-062 | Notificar al coordinador cuando hay planificaciones pendientes de su revisión. | Media |

## Reglas de Negocio

- **RN-01**: Una sola versión oficial vigente por (profesor, materia, período académico).
- **RN-02**: Una versión enviada no se modifica; se envía una nueva.
- **RN-03**: La aprobación requiere **doble visto** (moderadora + coordinador).
- **RN-04**: Una planificación oficial puede ser **reemplazada** (no eliminada). La anterior queda en histórico.
- **RN-05**: El período es **anual**, **1° cuatrimestre** o **2° cuatrimestre**, definido a inicio de año por el plan de estudios.
- **RN-06**: La ausencia de cualquiera de los 7 campos obligatorios provoca **rechazo automático**.
- **RN-07**: Errores leves pueden ser corregidos por la moderadora sin devolver al profesor; queda registrado.
- **RN-08**: Las entregas posteriores a la fecha límite se aceptan pero se marcan como **tardías**. Atrasos > 10–15 días son significativos para reportes de cumplimiento.
- **RN-09**: Cada profesor pertenece a una sola institución (ICES o UCSE) a efectos de notificación y plantilla.
- **RN-10**: Las materias anuales no requieren ratificación a mitad de año.
- **RN-11**: Una materia cuatrimestral dictada en ambos cuatrimestres requiere **una planificación por cuatrimestre**.

## No Funcionales

| ID | Categoría | Requerimiento |
|---|---|---|
| RNF-001 | Disponibilidad | Disponible en horario hábil, 99% mensual. |
| RNF-002 | Seguridad | Autenticación obligatoria; sesión con expiración. |
| RNF-003 | Seguridad | Roles diferenciados: profesor / coordinador / moderadora / alumnado / gestión / admin. |
| RNF-004 | Auditoría | Cada acción relevante (envío, aprobación, rechazo, corrección, reemplazo) se audita con autor y timestamp. |
| RNF-005 | Usabilidad | Validación de completitud en tiempo real (antes de enviar). |
| RNF-006 | Compatibilidad | Navegadores modernos (Chrome, Firefox, Edge últimas 2 versiones); responsive básico. |
| RNF-007 | Notificaciones | Envío de mails confiable, con reintentos ante fallos. |
| RNF-008 | Backup | Respaldo diario del repositorio de planificaciones. |
| RNF-009 | Integración | (A evaluar) integración o exportación con Google Drive para mantener compatibilidad operativa. |
| RNF-010 | Privacidad | Cumplimiento de normativa local de protección de datos personales. |
| RNF-011 | Configurabilidad | Fechas de instancias, audiencias, plantillas y materiales son administrables sin intervención de IT. |

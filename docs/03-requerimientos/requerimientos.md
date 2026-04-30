# Requerimientos Funcionales (preliminar)

> Cada RF se valida/ajusta tras las entrevistas. Trazar al CU y a la entrevista que lo origina.

| ID | Requerimiento | Prioridad | Origen | CU |
|---|---|---|---|---|
| RF-001 | El profesor podrá crear una planificación para un período determinado. | Alta | — | CU-01 |
| RF-002 | El profesor podrá adjuntar el documento de planificación (formato a definir). | Alta | — | CU-01 |
| RF-003 | El profesor podrá enviar la planificación al moderador. | Alta | — | CU-02 |
| RF-004 | El sistema generará automáticamente un número de versión correlativo por (profesor, materia, período). | Alta | — | CU-02 |
| RF-005 | El moderador podrá listar las planificaciones pendientes de revisión. | Alta | — | CU-05 |
| RF-006 | El moderador podrá aprobar una planificación. | Alta | — | CU-07 |
| RF-007 | El moderador podrá rechazar una planificación registrando observaciones. | Alta | — | CU-08 |
| RF-008 | El profesor podrá ver las observaciones de un rechazo. | Alta | — | CU-03 |
| RF-009 | El profesor podrá enviar una nueva versión tras un rechazo. | Alta | — | CU-04 |
| RF-010 | Al aprobar, el sistema marcará esa versión como **oficial** del período. | Alta | — | CU-07 |
| RF-011 | Solo puede existir **una** versión oficial por (profesor, materia, período). | Alta | RN-01 | — |
| RF-012 | El sistema notificará por mail los cambios de estado relevantes. | Media | — | varios |
| RF-013 | El sistema mantendrá histórico completo de versiones. | Alta | — | — |

# Reglas de Negocio (preliminar)

- **RN-01:** Una sola versión oficial por (profesor, materia, período).
- **RN-02:** Una versión enviada no se puede modificar; se debe enviar una nueva.
- **RN-03:** Solo el moderador asignado puede aprobar/rechazar.
- **RN-04:** Una vez aprobada, la planificación oficial no se puede borrar (a confirmar política de modificación).
- **RN-05:** El período es mensual; fecha límite de envío a definir.

# Requerimientos No Funcionales (preliminar)

| ID | Categoría | Requerimiento |
|---|---|---|
| RNF-001 | Disponibilidad | El sistema estará disponible en horario hábil al menos 99%. |
| RNF-002 | Seguridad | Autenticación obligatoria; cada acción auditada (quién, qué, cuándo). |
| RNF-003 | Seguridad | Roles y permisos diferenciados (profesor / moderador / admin). |
| RNF-004 | Usabilidad | El moderador debe poder revisar y resolver una planificación en menos de N clics (a definir). |
| RNF-005 | Compatibilidad | Soporte navegadores modernos (Chrome, Firefox, Edge últimas 2 versiones). |
| RNF-006 | Rendimiento | Listado de pendientes < 2s para volúmenes esperados. |
| RNF-007 | Trazabilidad | Toda transición de estado queda registrada con timestamp y autor. |
| RNF-008 | Backup | Respaldo diario del repositorio de planificaciones. |
| RNF-009 | Privacidad | Cumplimiento de normativa local de protección de datos personales. |

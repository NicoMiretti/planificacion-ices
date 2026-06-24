# Guía de Usuario — Coordinador
## Sistema de Planificaciones Académicas · ICES / UCSE

**Versión del documento:** 1.0  
**Fecha:** Junio 2026  
**Audiencia:** Coordinadores de Carrera (rol Coordinador)  
**URL del sistema:** http://190.13.88.96/planificaciones/

---

## Índice

1. [Acceso al sistema](#1-acceso-al-sistema)
2. [Panel de inicio](#2-panel-de-inicio)
3. [Tablero de revisión](#3-tablero-de-revisión)
4. [Revisar una planificación](#4-revisar-una-planificación)
5. [Dar visto bueno (aprobar)](#5-dar-visto-bueno-aprobar)
6. [Rechazar con observaciones](#6-rechazar-con-observaciones)
7. [Doble aprobación con la Secretaría Académica](#7-doble-aprobación-con-la-secretaría-académica)
8. [Consultar el estado de una convocatoria](#8-consultar-el-estado-de-una-convocatoria)
9. [Escenarios frecuentes](#9-escenarios-frecuentes)
10. [Preguntas frecuentes](#10-preguntas-frecuentes)

---

## 1. Acceso al sistema

Ingresar desde cualquier navegador a:

```
http://190.13.88.96/planificaciones/
```

| Campo | Valor |
|-------|-------|
| Email | matias.maretto@gmail.com |
| Contraseña | `Coord@Ices2026` (temporal — se recomienda cambiarla) |

> **Para cambiar la contraseña:** hacer clic en el nombre de usuario en la barra superior → *Mi perfil* → *Cambiar contraseña*.

---

## 2. Panel de inicio

Al ingresar, el sistema muestra un **panel de inicio** con un resumen del estado de revisión de las carreras a su cargo:

| Indicador | Significado |
|-----------|-------------|
| **Pendientes totales** | Planificaciones en revisión de sus carreras |
| **Esperando mi visto bueno** | Planificaciones que usted aún no revisó |
| **Ya di visto bueno** | Planificaciones donde ya aprobó, pero falta la Secretaría |
| **Entregas tardías** | Documentos enviados fuera de término |

Los indicadores son accesos directos al tablero de revisión con el filtro correspondiente.

---

## 3. Tablero de revisión

**Ruta:** Menú superior → *Revisión*

El tablero muestra todas las planificaciones **en estado "En Revisión"** que corresponden a las carreras que usted coordina. Las planificaciones de otras carreras no son visibles.

Cada fila muestra:
- Nombre del profesor y la materia.
- Carrera e instancia (convocatoria) a la que corresponde.
- Fecha de envío.
- Indicador de **entrega tardía** (marcado visualmente si fue enviado después de la fecha límite).
- Si usted ya dio su visto bueno en esa planificación.

**Filtros disponibles:**
- Por **carrera** (si coordina más de una)
- Por **entrega tardía**

> Las planificaciones se ordenan por fecha de envío: las más antiguas primero, para incentivar la revisión en orden de llegada.

---

## 4. Revisar una planificación

**Ruta:** Tablero → hacer clic en la fila de la planificación

La pantalla de revisión muestra:

1. **Datos del documento:** materia, profesor, carrera, convocatoria, número de versión.
2. **Botón de descarga** del archivo Word para leerlo.
3. **Estado de vistos buenos:** si usted ya aprobó, si la Secretaría ya aprobó, o si ambos aún falta.
4. **Secciones faltantes detectadas automáticamente** al momento del envío (si las hay): son campos que el sistema marcó como ausentes pero que el documento superó la validación automática de todas formas, o bien son un registro de advertencia.
5. **Historial completo** de la planificación: todas las versiones enviadas, rechazos anteriores, correcciones y aprobaciones.
6. **Acciones disponibles:** Dar visto bueno / Rechazar.

> **Importante:** El coordinador **no** puede aplicar correcciones leves. Esa acción es exclusiva de la Secretaría Académica (Moderadora).

---

## 5. Dar visto bueno (aprobar)

Cuando la planificación cumple con los requisitos académicos, hacer clic en el botón **"Dar visto bueno"**.

**Regla — Doble aprobación:**
- La planificación requiere el visto bueno de **dos revisores**: usted (coordinador) y la Secretaría Académica (moderadora).
- Pueden dar el visto bueno en **cualquier orden** e independientemente.
- Cuando **ambos** lo hayan dado, la planificación pasa automáticamente al estado **Oficial Vigente** y el proceso finaliza.
- Si solo uno lo dio, la planificación permanece en revisión y el sistema muestra quién falta.

> No puede dar el visto bueno dos veces sobre la misma versión. El sistema lo previene.

---

## 6. Rechazar con observaciones

Si la planificación presenta problemas de contenido que el profesor debe corregir:

1. Hacer clic en **"Rechazar"** en la vista de revisión.
2. Completar el campo de **observaciones** (obligatorio). Sea específico: indique qué sección o aspecto debe corregirse y, si es posible, cómo.
3. Confirmar la acción.

**Consecuencias del rechazo:**
- La versión pasa al estado **Rechazada**.
- El profesor deberá subir una **nueva versión** del documento.
- El proceso de revisión comienza de nuevo con esa nueva versión: tanto usted como la Secretaría deberán volver a revisar y dar el visto bueno.
- Su visto bueno anterior (si lo había dado) **no se conserva** para la nueva versión.

> Cualquiera de los dos revisores puede rechazar la planificación, independientemente de si el otro ya dio el visto bueno.

---

## 7. Doble aprobación con la Secretaría Académica

El proceso de doble aprobación garantiza que cada planificación sea revisada tanto por la Secretaría como por el responsable académico de la carrera. Aspectos a tener en cuenta:

**No hay orden obligatorio:** usted y la Secretaría pueden revisar en cualquier momento. No es necesario esperar a que el otro revise primero.

**Visibilidad compartida:** en la pantalla de revisión ambos pueden ver el estado actual (quién ya aprobó y quién no).

**Si la Secretaría aplica una corrección leve:** la planificación permanece en revisión y usted puede seguir dando su visto bueno normalmente. La corrección leve no afecta el estado del proceso desde su perspectiva.

**Si hay un rechazo:** no importa quién rechace — la versión queda invalidada para ambos y el profesor debe reenviar.

---

## 8. Consultar el estado de una convocatoria

**Ruta:** Menú superior → *Convocatorias* → [nombre de la convocatoria]

Como coordinador, puede ver el detalle de las convocatorias que incluyen sus carreras. La tabla muestra todas las materias de su carrera y el estado de cada planificación:

| Estado visible | Significado |
|----------------|-------------|
| Sin cargar | El profesor no subió nada |
| Borrador | Subido pero no enviado |
| En revisión | Aguardando revisión |
| Rechazada | Requiere corrección del profesor |
| Oficial vigente ✓ | Aprobada por ambos revisores |

Hacer clic en cualquier planificación lleva a la vista de revisión correspondiente.

---

## 9. Escenarios frecuentes

### La planificación tiene campos faltantes detectados automáticamente

Al ingresar a la vista de revisión puede ver listadas las secciones que el sistema detectó como faltantes al momento del envío. Sin embargo, si la planificación llegó al tablero en estado *En Revisión* significa que **superó la validación automática**. Los campos que ve listados son una advertencia informativa.

Si considera que el documento efectivamente no cumple los requisitos, puede rechazarlo con observaciones.

### Un profesor envió fuera de término

Las entregas tardías aparecen marcadas en el tablero. La decisión de aceptarlas o rechazarlas es académica y queda a su criterio junto con la Secretaría. El sistema no bloquea automáticamente las entregas tardías.

### Necesito revisar muchas planificaciones

Utilizar el filtro del tablero para ver solo las planificaciones de una carrera a la vez. El sistema ordena por antigüedad de envío: las más urgentes (enviadas hace más tiempo) aparecen primero.

### La Secretaría ya rechazó la planificación antes de que yo la revisara

En ese caso la planificación ya no está en el tablero: pasó al estado *Rechazada* y el profesor debe reenviar. Cuando el profesor envíe la nueva versión, volverá a aparecer en su tablero para revisión.

---

## 10. Preguntas frecuentes

**¿Puedo ver planificaciones de otras carreras?**  
No. Solo tiene acceso a las planificaciones de las carreras que usted coordina.

**¿Puedo aplicar correcciones leves al documento?**  
No. Esta acción es exclusiva de la Secretaría Académica (rol Moderadora).

**¿Qué pasa si rechazo una planificación que la Secretaría ya aprobó?**  
El rechazo anula el proceso completo: la versión pasa a *Rechazada* y el visto bueno de la Secretaría queda sin efecto. Cuando el profesor envíe la nueva versión, ambos deberán volver a revisarla.

**¿Puedo revocar mi visto bueno después de darlo?**  
No es posible directamente. Si detecta un problema después de haber aprobado, comuníquese con la Secretaría para coordinar un rechazo desde su cuenta.

**¿Recibiré notificaciones cuando lleguen nuevas planificaciones?**  
El sistema cuenta con un módulo de notificaciones. Consultar con el administrador si el envío de correos electrónicos está activo en el entorno actual.

**¿Puedo ver el historial de revisiones de convocatorias anteriores?**  
Sí. Desde *Convocatorias* puede acceder a instancias cerradas de años anteriores y ver el historial de cualquier planificación de sus carreras.

**¿Qué significa "Oficial Vigente"?**  
Significa que la planificación fue aprobada por ambos revisores (usted y la Secretaría) y es la versión definitiva para esa materia en esa convocatoria. No requiere ninguna acción adicional.

---

*Documento elaborado en base al código fuente del sistema. Versión 1.0 — Junio 2026.*

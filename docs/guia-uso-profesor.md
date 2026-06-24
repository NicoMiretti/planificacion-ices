# Guía de Usuario — Profesor
## Sistema de Planificaciones Académicas · ICES / UCSE

**Versión del documento:** 1.0  
**Fecha:** Junio 2026  
**Audiencia:** Docentes (rol Profesor)  
**URL del sistema:** http://190.13.88.96/planificaciones/

---

## Índice

1. [Acceso al sistema](#1-acceso-al-sistema)
2. [Panel de inicio](#2-panel-de-inicio)
3. [Mis convocatorias](#3-mis-convocatorias)
4. [Cargar una planificación](#4-cargar-una-planificación)
5. [Enviar la planificación a revisión](#5-enviar-la-planificación-a-revisión)
6. [Seguimiento del estado](#6-seguimiento-del-estado)
7. [Corregir una planificación rechazada](#7-corregir-una-planificación-rechazada)
8. [Clonar una planificación anterior](#8-clonar-una-planificación-anterior)
9. [Estados posibles](#9-estados-posibles)
10. [Preguntas frecuentes](#10-preguntas-frecuentes)

---

## 1. Acceso al sistema

Ingresar desde cualquier navegador a:

```
http://190.13.88.96/planificaciones/
```

Las credenciales son las asignadas por la Secretaría Académica:

| Campo | Valor |
|-------|-------|
| Email | su dirección de correo institucional (`nombre.apellido@ices.edu.ar`) |
| Contraseña | `Profe@Ices2026` (temporal — se recomienda cambiarla al primer ingreso) |

> **Para cambiar la contraseña:** hacer clic en el nombre de usuario en la barra superior → *Mi perfil* → *Cambiar contraseña*.

---

## 2. Panel de inicio

Al ingresar, el sistema muestra un **panel de inicio** con alertas personalizadas sobre el estado de sus planificaciones:

| Alerta | Qué significa |
|--------|---------------|
| 🔴 Planificación rechazada | Necesita corregir y reenviar el documento |
| 🟡 Borrador guardado | Subió el archivo pero todavía no lo envió a revisión |
| 🕐 En revisión | El documento fue enviado y está siendo revisado |
| ⚠️ Sin cargar | Tiene una materia asignada en una convocatoria activa y aún no subió nada |

Las alertas son accesos directos: hacer clic en cualquiera lleva a la planificación correspondiente.

---

## 3. Mis convocatorias

**Ruta:** Menú superior → *Mis Convocatorias*

Esta sección muestra todas las instancias de presentación (convocatorias) en las que el profesor tiene materias asignadas.

### Convocatorias activas

Se listan las convocatorias abiertas o programadas del año en curso. Para cada una se muestra un resumen del estado de las planificaciones:

| Contador | Significado |
|----------|-------------|
| Sin cargar | Materias con planificación pendiente de subir |
| Borrador | Documentos guardados pero no enviados |
| En revisión | Documentos enviados, aguardando revisión |
| Rechazadas | Documentos rechazados que requieren corrección |
| Oficiales | Planificaciones aprobadas |

Hacer clic en el nombre de una convocatoria muestra el **detalle** con la lista completa de materias asignadas y el estado de cada una.

### Convocatorias históricas

En la misma pantalla, más abajo, se muestran convocatorias de años anteriores o cerradas. Solo se pueden consultar; no se puede cargar ni enviar documentos en ellas.

---

## 4. Cargar una planificación

**Ruta:** Mis Convocatorias → [nombre de la convocatoria] → botón **Cargar planificación** junto a la materia correspondiente

### Requisitos previos

- La convocatoria debe estar en estado **Abierta** o **Programada** (en la fecha de apertura o posterior).
- No puede haber una versión de la misma materia **en revisión** en este momento. Si la hay, debe esperar el resultado de esa revisión.

### Pasos

1. Hacer clic en **Cargar planificación** en la fila de la materia.
2. En la pantalla de carga verá:
   - Los datos de la materia y la convocatoria.
   - Si existe un **tipo de planificación** asignado, verá las secciones obligatorias que el documento debe contener y un enlace a la documentación de referencia.
   - Si la institución tiene una **plantilla** disponible, habrá un botón para descargarla.
3. Hacer clic en **Seleccionar archivo** y elegir el documento Word (`.doc` o `.docx`) desde su equipo.
4. Hacer clic en **Guardar borrador**.

El documento queda guardado como **borrador**. Puede reemplazarlo tantas veces como necesite antes de enviarlo.

> **Si ya existe un borrador previo**, al guardar uno nuevo el sistema reemplaza el anterior automáticamente. Solo puede existir un borrador activo a la vez por materia.

---

## 5. Enviar la planificación a revisión

Guardar el borrador **no** lo envía a revisión. Para iniciar el proceso de aprobación se debe enviar explícitamente.

**Ruta:** Detalle de la planificación (clic en la materia desde la convocatoria) → botón **Enviar a revisión**

### Qué ocurre al enviar

1. El sistema analiza automáticamente el documento Word en busca de las **secciones obligatorias** definidas por el tipo de planificación.
2. **Si todas las secciones están presentes:** la planificación pasa al estado *En Revisión* y queda en manos de los revisores (Secretaría Académica y Coordinador de carrera).
3. **Si falta alguna sección:** la planificación se rechaza automáticamente y se muestra un mensaje con los campos faltantes. Deberá corregir el documento y volver a cargar una nueva versión.

### Entregas tardías

Si el envío se realiza **después de la fecha límite** de la convocatoria, el sistema lo acepta igualmente pero lo marca como **entrega tardía**. Esto queda registrado en el historial. Se recomienda respetar las fechas establecidas.

---

## 6. Seguimiento del estado

**Ruta:** Detalle de la planificación (haciendo clic en la materia desde la convocatoria)

La pantalla de detalle muestra:

1. **Estado actual** de la última versión.
2. **Historial de versiones** con todas las versiones enviadas, sus estados y fechas.
3. **Observaciones de rechazo** (si aplica): el texto que dejaron los revisores explicando por qué fue rechazada.
4. **Botón de descarga** del archivo de cada versión.
5. **Archivo de corrección** (si la Secretaría aplicó una corrección leve): disponible para descarga en el historial.

---

## 7. Corregir una planificación rechazada

Si su planificación fue rechazada (ya sea automáticamente o por un revisor), el proceso es:

1. Ir al detalle de la planificación.
2. Leer con atención las **observaciones** del rechazo (en el historial).
3. Corregir el documento Word en su computadora.
4. Volver a la planificación → botón **Cargar planificación** → subir el documento corregido → **Guardar borrador**.
5. Revisar que el documento esté correcto.
6. Hacer clic en **Enviar a revisión**.

> Cada envío genera una nueva versión numerada. El historial completo se conserva para consulta.

### Rechazada automáticamente vs. rechazada por revisor

| Tipo | Causa | Qué debe hacer |
|------|-------|----------------|
| **Rechazada automáticamente** | El sistema detectó que falta una o más secciones obligatorias en el documento | Agregar las secciones indicadas y reenviar |
| **Rechazada por revisor** | Un revisor (Secretaría o Coordinador) encontró problemas de contenido | Leer las observaciones y corregir según lo indicado |

---

## 8. Clonar una planificación anterior

Si ya tiene una planificación **oficial** de un período anterior para la misma materia, puede usarla como punto de partida para la convocatoria actual.

**Ruta:** Al abrir la pantalla de carga de una materia → sección **"Clonar planificación anterior"** (si está disponible)

El sistema lista las planificaciones oficiales previas de esa materia. Al seleccionar una y confirmar:
- Se crea un **borrador** en la convocatoria actual con el mismo documento.
- Puede editarlo antes de enviarlo a revisión.

> La clonación no envía automáticamente la planificación. Siempre debe revisar y enviar manualmente.

---

## 9. Estados posibles

| Estado | Qué significa | Acción requerida |
|--------|---------------|-----------------|
| **Sin cargar** | La materia está en la convocatoria pero no subió nada | Cargar el documento |
| **Borrador** | Documento guardado, no enviado | Enviar a revisión cuando esté listo |
| **En revisión** | Enviado, aguardando aprobación | Ninguna — esperar resultado |
| **Rechazada automáticamente** | Faltan secciones obligatorias en el documento | Corregir y reenviar |
| **Rechazada** | Un revisor la rechazó con observaciones | Leer observaciones, corregir y reenviar |
| **Oficial vigente** | Aprobada por ambos revisores | Ninguna — proceso completado ✓ |

---

## 10. Preguntas frecuentes

**¿Puedo modificar una planificación que ya envié a revisión?**  
No. Mientras la planificación esté *En Revisión* no puede cargarse una nueva versión. Debe esperar el resultado: si es rechazada, podrá corregir y reenviar; si es aprobada, el proceso finalizó.

**¿Qué formato debe tener el archivo?**  
El sistema acepta documentos Word (`.doc` o `.docx`). No se aceptan PDFs ni otros formatos.

**¿Qué son las "secciones obligatorias"?**  
Son los títulos o encabezados que el documento Word debe contener según el tipo de planificación definido por la Secretaría. El sistema busca esos textos en el documento al momento del envío. Si su archivo usa los títulos correctos y aun así es rechazado, comunicarse con la Secretaría.

**¿Dónde descargo la plantilla?**  
Si la institución tiene una plantilla disponible, aparecerá un botón de descarga en la pantalla de carga de la planificación. También puede solicitarla a la Secretaría Académica.

**¿Puedo ver las planificaciones de otros profesores?**  
No. Solo tiene acceso a sus propias planificaciones.

**¿Qué pasa si tengo materias en más de una carrera?**  
Todas sus materias asignadas como titular aparecerán en la pantalla de Mis Convocatorias. Deberá cargar una planificación por cada materia que figure en cada convocatoria activa.

**¿Puedo entregar fuera de término?**  
El sistema acepta entregas fuera de término pero las marca como **tardías**. La decisión de aceptarlas o no queda a criterio de la Secretaría Académica.

**¿Cómo sé si mi planificación fue aprobada definitivamente?**  
El estado cambiará a **Oficial vigente** en el detalle de la planificación y en el panel de inicio desaparecerá la alerta correspondiente.

---

*Documento elaborado en base al código fuente del sistema. Versión 1.0 — Junio 2026.*

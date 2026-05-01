# Casos de Uso — Sistema de Planificaciones ICES/UCSE

> Referencia: [requerimientos.md](../03-requerimientos/requerimientos.md) · [actores.md](actores.md) · [diagrama-estados-planificacion.md](../05-modelo/diagrama-estados-planificacion.md)

---

## CU-01 — Crear instancia de presentación

**ID:** CU-01  
**Nombre:** Crear instancia de presentación  
**Actor primario:** Moderadora  
**Actores secundarios:** Sistema de notificaciones  
**Stakeholders e intereses:**
- Moderadora: necesita abrir períodos de carga con fechas y audiencia definida.
- Profesores: necesitan saber cuándo y qué deben presentar.

**Precondiciones:**
- La moderadora está autenticada con rol `moderadora`.
- Existen carreras, materias y profesores cargados en el sistema (catálogo actualizado).

**Postcondiciones (éxito):**
- Se crea la instancia con estado "programada" o "abierta" según fecha de apertura.
- Los profesores de la audiencia reciben notificación por mail al llegar la fecha de apertura.
- La instancia queda registrada en el histórico de instancias del sistema.

**Disparador:** La moderadora decide abrir un período de carga de planificaciones (ej. inicio de año, inicio de cuatrimestre).

### Flujo principal (camino feliz)
1. La moderadora selecciona "Crear instancia de presentación".
2. El sistema presenta el formulario con los campos: nombre, período cubierto (anual/1°cuat/2°cuat), año académico, audiencia (carreras, institución, régimen de materias), fecha de apertura, fecha límite.
3. La moderadora completa los campos y selecciona la plantilla vigente (ICES o UCSE) y los materiales de apoyo a adjuntar.
4. La moderadora confirma la creación.
5. El sistema valida los datos y crea la instancia.
6. Si la fecha de apertura es inmediata, el sistema dispara el envío de mails a los profesores de la audiencia, agrupados por institución.
7. El sistema confirma la creación exitosa.

### Flujos alternativos
**A1.** Fecha de apertura futura  
1. El sistema agenda la instancia como "programada".
2. Al llegar la fecha de apertura, el sistema automáticamente cambia el estado a "abierta" y dispara las notificaciones.

**A2.** Instancias paralelas  
1. El sistema permite crear múltiples instancias activas simultáneamente (ej. anuales + cuatrimestrales).
2. Cada profesor ve solo las instancias que le corresponden según su audiencia.

### Flujos de excepción
**E1.** Audiencia vacía  
1. El sistema advierte que ningún profesor coincide con los criterios de audiencia.
2. La moderadora ajusta los filtros o cancela.

**E2.** Fecha límite anterior a fecha de apertura  
1. El sistema rechaza la creación indicando el error.

### Reglas de negocio aplicables
- RF-010, RF-011, RF-012, RF-013, RNF-011

### Requerimientos relacionados
- RF-010, RF-011, RF-012, RF-013, RF-014

### Frecuencia / Volumen
- ~4-6 instancias por año (anuales en marzo, cuatrimestrales en marzo y julio, excepcionales).

### Notas / Cuestiones abiertas
- Las instancias de años anteriores quedan almacenadas en el histórico para consulta y auditoría.

---

## CU-02 — Consultar tablero de revisión

**ID:** CU-02  
**Nombre:** Consultar tablero de revisión  
**Actor primario:** Moderadora / Coordinador  
**Actores secundarios:** —  
**Stakeholders e intereses:**
- Moderadora: necesita visión global del estado de planificaciones.
- Coordinador: necesita ver las planificaciones de su carrera/área pendientes de revisión.

**Precondiciones:**
- El usuario está autenticado con rol `moderadora` o `coordinador`.
- Existen planificaciones enviadas en alguna instancia.

**Postcondiciones (éxito):**
- El usuario visualiza la lista de planificaciones filtrada según sus permisos.

**Disparador:** El usuario accede al tablero de revisión.

### Flujo principal (camino feliz)
1. El usuario selecciona "Tablero de revisión".
2. El sistema presenta la lista de planificaciones con columnas: profesor, materia, carrera, año, instancia, estado, fecha envío, marca tardía (Sí/No), acciones.
3. El usuario puede filtrar por: carrera, año de cursado, materia, estado (enviada, en revisión, rechazada, aprobada), institución, instancia, año académico.
4. El usuario puede ordenar por cualquier columna.
5. El usuario selecciona una planificación para ver detalle o tomar acción.

### Flujos alternativos
**A1.** Coordinador consulta  
1. El sistema muestra solo las planificaciones correspondientes a las carreras/áreas asignadas al coordinador.

**A2.** Filtro por instancias históricas  
1. El usuario puede seleccionar instancias de años anteriores para consultar el histórico.

### Flujos de excepción
**E1.** Sin resultados  
1. El sistema indica que no hay planificaciones que coincidan con los filtros.

### Reglas de negocio aplicables
- RF-030, RF-031, RF-053

### Requerimientos relacionados
- RF-030, RF-031, RF-053

### Frecuencia / Volumen
- Acceso diario durante los períodos de carga; esporádico el resto del año.

### Notas / Cuestiones abiertas
- El histórico de rechazos solo es visible para moderadora y coordinador correspondiente.

---

## CU-03 — Aprobar planificación

**ID:** CU-03  
**Nombre:** Aprobar planificación  
**Actor primario:** Moderadora, Coordinador  
**Actores secundarios:** Sistema de notificaciones  
**Stakeholders e intereses:**
- Moderadora: valida cumplimiento de formato y contenido general.
- Coordinador: valida pertinencia académica para su carrera.
- Profesor: espera confirmación de que su planificación fue aceptada.

**Precondiciones:**
- La planificación está en estado "En revisión".
- El usuario está autenticado con rol correspondiente.
- (Para aprobación final) Falta solo el visto del actor actual.

**Postcondiciones (éxito):**
- Si es aprobación parcial: se registra el visto del actor; la planificación espera el segundo visto.
- Si es doble aprobación: la planificación pasa a estado "Aprobada" y luego a "Oficial vigente".
- El profesor recibe notificación de aprobación.
- Si existía una versión oficial anterior, pasa a estado "Reemplazada" y queda en histórico.

**Disparador:** Moderadora o coordinador decide aprobar una planificación revisada.

### Flujo principal (camino feliz)
1. El usuario accede a la planificación desde el tablero.
2. El sistema muestra el documento Word de la planificación y los datos: profesor, materia, versión, fecha envío, marca tardía.
3. El usuario descarga/visualiza el documento Word.
4. El usuario verifica el contenido y selecciona "Aprobar".
5. El sistema registra el visto del actor con timestamp.
6. Si ya existe el visto del otro rol (doble aprobación):
   - El sistema cambia el estado a "Aprobada" → "Oficial vigente".
   - El sistema notifica al profesor.
   - Si había una versión oficial previa, pasa a "Reemplazada".
7. El sistema confirma la operación.

### Flujos alternativos
**A1.** Aprobación parcial (falta el otro visto)  
1. El sistema registra el visto y mantiene el estado "En revisión - pendiente [rol faltante]".
2. Opcionalmente notifica al rol faltante que hay una planificación esperando su revisión.

### Flujos de excepción
**E1.** Usuario intenta aprobar sin permiso sobre esa carrera  
1. El sistema rechaza la acción indicando falta de permisos.

### Reglas de negocio aplicables
- RN-01, RN-03, RN-04

### Requerimientos relacionados
- RF-032, RF-040, RF-041, RF-042, RF-061

### Frecuencia / Volumen
- Decenas a cientos de aprobaciones por instancia.

### Notas / Cuestiones abiertas
- La doble aprobación es obligatoria (RN-03).

---

## CU-04 — Rechazar planificación

**ID:** CU-04  
**Nombre:** Rechazar planificación  
**Actor primario:** Moderadora / Coordinador  
**Actores secundarios:** Sistema de notificaciones  
**Stakeholders e intereses:**
- Moderadora/Coordinador: necesitan devolver planificaciones con problemas.
- Profesor: necesita saber qué debe corregir.

**Precondiciones:**
- La planificación está en estado "En revisión".
- El usuario está autenticado con rol correspondiente.

**Postcondiciones (éxito):**
- La planificación pasa a estado "Rechazada".
- Se registran las observaciones del rechazo.
- El profesor recibe notificación con las observaciones.
- La versión queda en el histórico con el motivo de rechazo.

**Disparador:** El revisor detecta problemas que requieren corrección por parte del profesor.

### Flujo principal (camino feliz)
1. El usuario accede a la planificación desde el tablero.
2. El usuario revisa el documento Word.
3. El usuario selecciona "Rechazar".
4. El sistema solicita observaciones (texto libre obligatorio).
5. El usuario ingresa las observaciones detallando qué debe corregirse.
6. El usuario confirma el rechazo.
7. El sistema cambia el estado a "Rechazada" y registra observaciones, autor y timestamp.
8. El sistema notifica al profesor por mail incluyendo las observaciones.

### Flujos alternativos
**A1.** Rechazo con sugerencia de acción  
1. El usuario puede indicar campos específicos a revisar (ej. "Bibliografía incompleta", "Falta metodología").

### Flujos de excepción
**E1.** Observaciones vacías  
1. El sistema no permite rechazar sin observaciones.

### Reglas de negocio aplicables
- RN-02 (la versión enviada no se modifica; se envía una nueva)

### Requerimientos relacionados
- RF-033, RF-043, RF-061

### Frecuencia / Volumen
- Variable según calidad de entregas; típicamente 10-30% de envíos requieren al menos un rechazo.

### Notas / Cuestiones abiertas
- El histórico de rechazos es visible solo para moderadora y coordinador (RF-053).

---

## CU-05 — Aplicar corrección leve

**ID:** CU-05  
**Nombre:** Aplicar corrección leve  
**Actor primario:** Moderadora  
**Actores secundarios:** Sistema de notificaciones  
**Stakeholders e intereses:**
- Moderadora: necesita corregir errores menores sin devolver al profesor.
- Profesor: es informado de la corrección realizada.

**Precondiciones:**
- La planificación está en estado "En revisión".
- El error es leve (formato, tipográfico) y no afecta el contenido académico.

**Postcondiciones (éxito):**
- Se aplica la corrección al documento.
- La corrección queda registrada en el histórico con detalle de qué se modificó.
- El profesor es notificado de la corrección aplicada.
- La planificación continúa en estado "En revisión" (no se devuelve).

**Disparador:** La moderadora detecta un error menor que puede corregir directamente.

### Flujo principal (camino feliz)
1. La moderadora accede a la planificación en revisión.
2. La moderadora identifica un error leve (ej. formato de bibliografía, error tipográfico).
3. La moderadora selecciona "Aplicar corrección leve".
4. El sistema solicita descripción de la corrección.
5. La moderadora describe qué se corrigió.
6. La moderadora sube la versión corregida del documento Word o indica la corrección.
7. El sistema registra la corrección en el histórico (autor, timestamp, descripción).
8. El sistema notifica al profesor que se aplicó una corrección.
9. La planificación continúa el flujo de revisión sin devolverse.

### Flujos de excepción
**E1.** Corrección requiere intervención del profesor  
1. Si el cambio es sustancial, la moderadora debe usar CU-04 (Rechazar) en su lugar.

### Reglas de negocio aplicables
- RN-07

### Requerimientos relacionados
- RF-034, RF-043, RF-061

### Frecuencia / Volumen
- Ocasional; depende de la calidad de las entregas.

### Notas / Cuestiones abiertas
- Queda a criterio de la moderadora determinar qué es "leve".

---

## CU-06 — Ver instancias asignadas

**ID:** CU-06  
**Nombre:** Ver instancias asignadas  
**Actor primario:** Profesor  
**Actores secundarios:** —  
**Stakeholders e intereses:**
- Profesor: necesita saber qué planificaciones debe presentar y en qué plazos.

**Precondiciones:**
- El profesor está autenticado.
- Existe al menos una instancia abierta que incluye materias del profesor.

**Postcondiciones (éxito):**
- El profesor visualiza las instancias y materias donde debe presentar planificación.

**Disparador:** El profesor accede al sistema.

### Flujo principal (camino feliz)
1. El profesor accede a su panel principal.
2. El sistema muestra las instancias de presentación activas donde el profesor tiene materias asignadas.
3. Para cada instancia se muestra: nombre, período, fecha límite, materias a presentar, estado de cada materia (pendiente/enviada/en revisión/aprobada/rechazada), marca tardía si aplica.
4. El profesor puede seleccionar una materia para cargar o ver el estado de su planificación.

### Flujos alternativos
**A1.** Consulta de instancias pasadas  
1. El profesor puede acceder al histórico de instancias de años anteriores para consultar sus entregas previas.

**A2.** Sin instancias activas  
1. El sistema indica que no hay instancias abiertas actualmente.
2. El profesor puede consultar el histórico.

### Reglas de negocio aplicables
- RF-020

### Requerimientos relacionados
- RF-020, RF-028

### Frecuencia / Volumen
- Acceso frecuente durante los períodos de carga.

### Notas / Cuestiones abiertas
- —

---

## CU-07 — Cargar planificación

**ID:** CU-07  
**Nombre:** Cargar planificación  
**Actor primario:** Profesor  
**Actores secundarios:** —  
**Stakeholders e intereses:**
- Profesor: necesita completar la planificación según la plantilla institucional.

**Precondiciones:**
- El profesor está autenticado.
- Existe una instancia abierta para la materia.
- El profesor tiene acceso a la plantilla de su institución (ICES o UCSE).

**Postcondiciones (éxito):**
- El documento Word de la planificación queda guardado como borrador en el sistema.
- El profesor puede continuar editando o proceder al envío.

**Disparador:** El profesor decide comenzar o continuar la carga de una planificación.

### Flujo principal (camino feliz)
1. El profesor selecciona la materia e instancia donde desea cargar la planificación.
2. El sistema muestra la plantilla correspondiente a la institución del profesor (ICES o UCSE) y los materiales de apoyo (reglamento, calendario, guía APA, documento orientador).
3. El profesor descarga la plantilla Word.
4. El profesor completa la planificación offline en el documento Word según los 7 campos obligatorios:
   - Propósito
   - Fundamentación
   - Contenidos mínimos
   - Metodología
   - Requisitos para regularizar y promocionar
   - Criterios y formatos de evaluación
   - Bibliografía
5. El profesor sube el documento Word completado al sistema.
6. El sistema guarda el documento como borrador asociado a (profesor, materia, instancia).
7. El sistema confirma que el borrador fue guardado.

### Flujos alternativos
**A1.** Continuar borrador existente  
1. El profesor selecciona un borrador previamente guardado.
2. El sistema permite descargar, modificar y volver a subir.

**A2.** Usar clon de planificación anterior (ver CU-14)  
1. El profesor parte de una copia de una planificación oficial previa.

### Flujos de excepción
**E1.** Formato de archivo inválido  
1. El sistema solo acepta archivos .doc o .docx.
2. Se rechaza otro formato indicando el error.

### Reglas de negocio aplicables
- RF-021, RN-09

### Requerimientos relacionados
- RF-021, RF-004

### Frecuencia / Volumen
- Cada profesor carga 1-N planificaciones por instancia según sus materias asignadas.

### Notas / Cuestiones abiertas
- El documento es formato Word, respetando la plantilla institucional.

---

## CU-08 — Enviar planificación

**ID:** CU-08  
**Nombre:** Enviar planificación  
**Actor primario:** Profesor  
**Actores secundarios:** Validador automático de campos, Sistema de notificaciones  
**Stakeholders e intereses:**
- Profesor: necesita enviar su planificación al circuito de revisión.
- Moderadora: necesita recibir planificaciones completas.

**Precondiciones:**
- Existe un borrador cargado para la materia e instancia.
- La instancia está abierta (o cerrada pero acepta entregas tardías).

**Postcondiciones (éxito):**
- La planificación pasa de "Borrador" a "Enviada".
- Se asigna número de versión correlativo.
- Si la fecha es posterior a la fecha límite, se marca como "entrega tardía".
- Se notifica a la secretaría que llegó una planificación nueva.

**Postcondiciones (rechazo automático):**
- Si falta algún campo obligatorio, la planificación pasa a "Rechazada automáticamente".
- El profesor ve qué campos faltan.

**Disparador:** El profesor confirma el envío de su planificación.

### Flujo principal (camino feliz)
1. El profesor selecciona el borrador y elige "Enviar planificación".
2. El sistema ejecuta la **validación automática** verificando la presencia de los 7 campos obligatorios en el documento Word.
3. Validación exitosa: todos los campos están presentes.
4. El sistema asigna número de versión correlativo (ej. v1, v2, v3...) para (profesor, materia, período).
5. El sistema verifica la fecha actual contra la fecha límite de la instancia:
   - Si fecha actual ≤ fecha límite → entrega en tiempo.
   - Si fecha actual > fecha límite → se marca como **entrega tardía**.
6. El sistema cambia el estado a "Enviada".
7. El sistema notifica a la secretaría/moderadora que llegó una nueva planificación.
8. El sistema confirma al profesor el envío exitoso, mostrando el número de versión y si fue tardía.

### Flujos alternativos
**A1.** Entrega tardía  
1. El sistema permite el envío pero marca la versión como tardía.
2. La marca de tardía queda visible en el historial y reportes.
3. No se bloquea el envío.

### Flujos de excepción
**E1.** Validación fallida (campo faltante)  
1. El sistema detecta que falta al menos un campo obligatorio.
2. El sistema rechaza automáticamente el envío (estado "Rechazada automáticamente").
3. El sistema muestra al profesor qué campo(s) faltan.
4. El profesor debe corregir y volver a intentar (vuelve a CU-07).

### Reglas de negocio aplicables
- RN-02, RN-06, RN-08

### Requerimientos relacionados
- RF-022, RF-023, RF-024, RF-025, RF-027, RF-060

### Frecuencia / Volumen
- Cada profesor envía al menos una versión por materia por instancia.

### Notas / Cuestiones abiertas
- La marca de entrega tardía es solo informativa (fecha), no existe esquema de cumplimientos adicional.

---

## CU-09 — Ver observaciones

**ID:** CU-09  
**Nombre:** Ver observaciones  
**Actor primario:** Profesor  
**Actores secundarios:** —  
**Stakeholders e intereses:**
- Profesor: necesita conocer los motivos de rechazo o correcciones aplicadas.

**Precondiciones:**
- El profesor está autenticado.
- Existe al menos una planificación con observaciones (rechazada o con corrección leve).

**Postcondiciones (éxito):**
- El profesor visualiza las observaciones y el historial de su planificación.

**Disparador:** El profesor accede a una planificación con observaciones.

### Flujo principal (camino feliz)
1. El profesor selecciona una planificación desde su panel.
2. El sistema muestra el estado actual y el historial de versiones.
3. Para cada versión se muestra: número de versión, fecha envío, estado, observaciones (si hay), autor de las observaciones, correcciones leves aplicadas.
4. El profesor puede descargar cualquier versión del documento Word para comparar.

### Flujos alternativos
**A1.** Sin observaciones  
1. Si la planificación fue aprobada sin rechazos, se muestra el historial sin observaciones negativas.

### Reglas de negocio aplicables
- RF-028, RF-043

### Requerimientos relacionados
- RF-028, RF-043

### Frecuencia / Volumen
- Acceso tras cada notificación de rechazo o corrección.

### Notas / Cuestiones abiertas
- —

---

## CU-10 — Reenviar nueva versión

**ID:** CU-10  
**Nombre:** Reenviar nueva versión  
**Actor primario:** Profesor  
**Actores secundarios:** Validador automático de campos, Sistema de notificaciones  
**Stakeholders e intereses:**
- Profesor: necesita corregir y reenviar tras un rechazo.
- Moderadora/Coordinador: esperan recibir la versión corregida.

**Precondiciones:**
- Existe una planificación en estado "Rechazada" o "Rechazada automáticamente".
- La instancia aún acepta envíos (o están habilitadas las entregas tardías).

**Postcondiciones (éxito):**
- Se crea una nueva versión de la planificación.
- La versión anterior queda en el histórico.
- La nueva versión pasa por el flujo de validación y envío (CU-08).

**Disparador:** El profesor decide corregir y reenviar una planificación rechazada.

### Flujo principal (camino feliz)
1. El profesor accede a la planificación rechazada.
2. El profesor puede descargar la versión rechazada o la plantilla vacía.
3. El profesor corrige el documento Word según las observaciones.
4. El profesor sube el documento corregido.
5. El sistema guarda como nuevo borrador.
6. El profesor ejecuta CU-08 (Enviar planificación).
7. El sistema asigna nuevo número de versión correlativo.
8. La versión anterior permanece en el histórico.

### Flujos alternativos
**A1.** Partir de la versión rechazada  
1. El profesor descarga la versión rechazada, la modifica y la sube como nueva.

### Reglas de negocio aplicables
- RN-02

### Requerimientos relacionados
- RF-024, RF-025, RF-043

### Frecuencia / Volumen
- Variable; depende de la tasa de rechazos.

### Notas / Cuestiones abiertas
- Las versiones rechazadas quedan en el histórico con sus observaciones.

---

## CU-11 — Consultar planificación oficial vigente

**ID:** CU-11  
**Nombre:** Consultar planificación oficial vigente  
**Actor primario:** Alumnado / Secretarías generales / Equipo de gestión  
**Actores secundarios:** —  
**Stakeholders e intereses:**
- Alumnado: necesita consultar la planificación de sus materias.
- Secretarías/Gestión: necesitan acceder a las planificaciones oficiales para auditorías, homologaciones, etc.

**Precondiciones:**
- El usuario está autenticado (o tiene acceso público según configuración).
- Existe una versión oficial vigente para la materia consultada.

**Postcondiciones (éxito):**
- El usuario visualiza y puede descargar el documento Word de la planificación oficial.

**Disparador:** El usuario busca la planificación de una materia.

### Flujo principal (camino feliz)
1. El usuario accede a la pantalla principal de consulta.
2. El sistema presenta la estructura: **Carrera → Año de cursado → Materia**.
3. El usuario navega o busca la materia deseada.
4. El sistema muestra para cada materia: nombre, profesor, estado (oficial vigente / pendiente), período.
5. El usuario selecciona una materia con oficial vigente.
6. El sistema muestra los datos de la planificación oficial y permite descargar el documento Word.

### Flujos alternativos
**A1.** Consulta de años anteriores  
1. El usuario puede seleccionar un año académico anterior.
2. El sistema muestra las planificaciones oficiales de ese período histórico.

**A2.** Sin versión oficial  
1. El sistema indica que la materia no tiene planificación oficial vigente aún.

**A3.** Descarga por secretaría/gestión  
1. Los usuarios con rol gestión pueden descargar múltiples planificaciones en lote (a evaluar).

### Reglas de negocio aplicables
- RN-01

### Requerimientos relacionados
- RF-050, RF-051, RF-052

### Frecuencia / Volumen
- Acceso frecuente por alumnado al inicio de cursada; ocasional por gestión.

### Notas / Cuestiones abiertas
- El histórico de años anteriores permanece disponible para consulta.

---

## CU-12 — Cerrar revisión por consenso

**ID:** CU-12  
**Nombre:** Cerrar revisión por consenso  
**Actor primario:** Moderadora, Coordinador  
**Actores secundarios:** Sistema de notificaciones  
**Stakeholders e intereses:**
- Moderadora/Coordinador: necesitan resolver casos donde las idas y vueltas se prolongan excesivamente.
- Profesor: es notificado de la decisión.

**Precondiciones:**
- La planificación está en estado "En revisión" o "Rechazada".
- Ha habido múltiples ciclos de rechazo/reenvío sin resolución.
- Moderadora y coordinador acuerdan cerrar el ciclo.

**Postcondiciones (éxito):**
- La planificación pasa a estado "Aprobada" (por consenso) o queda documentado el cierre sin aprobación.
- Se registra el motivo del cierre forzado.
- El profesor es notificado.

**Disparador:** Los revisores deciden dar por cerrado un ciclo prolongado.

### Flujo principal (camino feliz)
1. La moderadora o coordinador identifica un caso con múltiples rechazos.
2. El usuario selecciona "Cerrar revisión por consenso".
3. El sistema solicita confirmación del otro revisor (doble autorización).
4. Ambos confirman el cierre.
5. El sistema solicita el motivo y la decisión: aprobar a pesar de deficiencias menores / cerrar sin aprobar (la materia queda sin oficial).
6. El sistema registra la decisión con timestamp, autores y motivo.
7. Si se aprueba: la planificación pasa a "Oficial vigente".
8. El sistema notifica al profesor.

### Flujos alternativos
**A1.** Cierre sin aprobación  
1. La materia queda registrada como "sin planificación oficial" para ese período.
2. Se documenta el caso para seguimiento.

### Flujos de excepción
**E1.** Falta confirmación del segundo revisor  
1. El sistema no permite el cierre unilateral; requiere doble autorización.

### Reglas de negocio aplicables
- RF-035

### Requerimientos relacionados
- RF-035

### Frecuencia / Volumen
- Excepcional; casos problemáticos.

### Notas / Cuestiones abiertas
- Definir cuántos ciclos de rechazo justifican esta acción.

---

## CU-13 — Reemplazar planificación oficial

**ID:** CU-13  
**Nombre:** Reemplazar planificación oficial  
**Actor primario:** Profesor  
**Actores secundarios:** Moderadora, Coordinador, Sistema de notificaciones  
**Stakeholders e intereses:**
- Profesor: necesita actualizar una planificación ya aprobada.
- Moderadora/Coordinador: deben aprobar la nueva versión.
- Alumnado: accederá a la versión actualizada.

**Precondiciones:**
- Existe una versión oficial vigente para (profesor, materia, período).
- El profesor está autenticado.

**Postcondiciones (éxito):**
- La nueva versión pasa por el circuito de aprobación.
- Al aprobarse, la anterior pasa a estado "Reemplazada" y queda en histórico.
- La nueva versión se convierte en "Oficial vigente".

**Disparador:** El profesor necesita modificar una planificación ya aprobada (ej. cambio de bibliografía, ajuste de cronograma).

### Flujo principal (camino feliz)
1. El profesor selecciona la planificación oficial vigente.
2. El profesor elige "Modificar planificación".
3. El sistema crea un nuevo borrador basado en la versión oficial (o permite subir uno nuevo).
4. El profesor realiza las modificaciones en el documento Word.
5. El profesor sube el documento modificado.
6. El profesor envía la nueva versión (ejecuta CU-08).
7. La nueva versión pasa por el circuito de revisión y aprobación (CU-03).
8. Al lograr doble aprobación:
   - La versión anterior pasa a "Reemplazada".
   - La nueva versión pasa a "Oficial vigente".
9. El sistema registra ambas versiones en el histórico.

### Flujos alternativos
**A1.** Nueva versión rechazada  
1. La versión oficial anterior permanece vigente.
2. El profesor puede corregir y reenviar.

### Reglas de negocio aplicables
- RN-01, RN-02, RN-04

### Requerimientos relacionados
- RF-042, RF-043

### Frecuencia / Volumen
- Ocasional; cambios durante el período académico.

### Notas / Cuestiones abiertas
- La versión reemplazada queda en el histórico identificable.

---

## CU-14 — Clonar planificación oficial previa

**ID:** CU-14  
**Nombre:** Clonar planificación oficial previa  
**Actor primario:** Profesor  
**Actores secundarios:** —  
**Stakeholders e intereses:**
- Profesor: necesita reutilizar una planificación anterior como punto de partida.

**Precondiciones:**
- El profesor está autenticado.
- Existe una planificación oficial de un período anterior para la misma materia.

**Postcondiciones (éxito):**
- Se crea un borrador basado en la planificación clonada.
- El profesor puede modificarlo antes de enviar.

**Disparador:** El profesor quiere partir de una planificación previa en lugar de la plantilla vacía.

### Flujo principal (camino feliz)
1. El profesor accede a cargar planificación para una materia e instancia.
2. El profesor selecciona "Clonar de período anterior".
3. El sistema muestra las planificaciones oficiales anteriores de esa materia (de años/períodos previos).
4. El profesor selecciona la versión a clonar.
5. El sistema crea una copia del documento Word como borrador.
6. El profesor descarga, modifica según el nuevo período, y sube la versión actualizada.
7. El profesor continúa con CU-08 (Enviar).

### Flujos alternativos
**A1.** Sin planificaciones previas  
1. El sistema indica que no hay versiones oficiales anteriores para clonar.
2. El profesor debe usar la plantilla vacía.

### Reglas de negocio aplicables
- RF-026

### Requerimientos relacionados
- RF-026

### Frecuencia / Volumen
- Común para materias que se repiten año a año.

### Notas / Cuestiones abiertas
- El clon es un punto de partida; debe actualizarse según el nuevo período.

---

## CU-15 — Generar reporte de cumplimiento de plazos

**ID:** CU-15  
**Nombre:** Generar reporte de cumplimiento de plazos  
**Actor primario:** Moderadora / Secretarías generales / Equipo de gestión  
**Actores secundarios:** —  
**Stakeholders e intereses:**
- Gestión: necesita datos de cumplimiento para evaluaciones docentes.
- Moderadora: seguimiento del proceso de carga.

**Precondiciones:**
- El usuario está autenticado con rol moderadora o gestión.
- Existen instancias con entregas registradas.

**Postcondiciones (éxito):**
- El usuario obtiene un reporte filtrable con datos de cumplimiento.

**Disparador:** El usuario necesita información sobre entregas a tiempo vs. tardías.

### Flujo principal (camino feliz)
1. El usuario accede a "Reportes" → "Cumplimiento de plazos".
2. El sistema presenta filtros: instancia, año académico, carrera, institución, profesor.
3. El usuario selecciona los filtros deseados.
4. El sistema genera el reporte mostrando para cada profesor/materia:
   - Fecha límite de la instancia.
   - Fecha de envío de la versión (primera y/o aprobada).
   - Marca: En tiempo / Tardía.
   - Días de atraso (si aplica).
5. El usuario puede exportar el reporte (Excel, PDF).

### Flujos alternativos
**A1.** Reporte consolidado  
1. El usuario puede ver un resumen: total entregas, % en tiempo, % tardías, promedio de días de atraso.

**A2.** Histórico de años anteriores  
1. El usuario puede generar reportes de instancias de años pasados.

### Reglas de negocio aplicables
- RN-08 (entregas tardías se aceptan pero se marcan)

### Requerimientos relacionados
- RF-054

### Frecuencia / Volumen
- Periódico; tras cierre de instancias o para evaluaciones.

### Notas / Cuestiones abiertas
- El reporte solo indica si fue en tiempo o tardía (con fecha); no existe un esquema de cumplimientos con puntajes o categorías adicionales.

---

## CU-16 — Gestionar catálogos

**ID:** CU-16  
**Nombre:** Gestionar catálogos  
**Actor primario:** Administrador (puede ser la Moderadora)  
**Actores secundarios:** —  
**Stakeholders e intereses:**
- Administrador: necesita mantener actualizados los datos maestros del sistema.
- Todos los usuarios: dependen de catálogos correctos.

**Precondiciones:**
- El usuario está autenticado con rol `admin` o `moderadora`.

**Postcondiciones (éxito):**
- Los catálogos quedan actualizados.
- Los cambios se reflejan en las instancias futuras.

**Disparador:** Inicio de año académico o cambios en carreras/materias/profesores.

### Flujo principal (camino feliz)
1. El administrador accede a "Gestión de catálogos".
2. El sistema presenta las opciones: Carreras, Materias, Profesores, Plantillas, Materiales de apoyo.
3. El administrador selecciona el catálogo a gestionar.

**Subcaso: Gestionar carreras**
1. El administrador puede agregar, editar o dar de baja carreras.
2. Cada carrera tiene: nombre, institución (ICES/UCSE), coordinador asignado, estado (activa/inactiva).

**Subcaso: Gestionar materias**
1. El administrador puede agregar, editar o dar de baja materias.
2. Cada materia tiene: nombre, carrera, año de cursado, régimen (anual/1°cuat/2°cuat), profesor titular, estado.
3. El sistema carga el listado anual según el plan de estudios.

**Subcaso: Gestionar profesores**
1. El administrador puede agregar, editar o dar de baja profesores.
2. Cada profesor tiene: nombre, email, institución (ICES/UCSE), estado.

**Subcaso: Gestionar plantillas**
1. El administrador sube las plantillas Word vigentes (una por institución).
2. Las plantillas incluyen los 7 campos obligatorios.

**Subcaso: Gestionar materiales de apoyo**
1. El administrador sube/actualiza los materiales: reglamento, calendario, guía APA, documento orientador.

### Flujos de excepción
**E1.** Intento de eliminar carrera/materia con histórico  
1. El sistema no permite eliminación; solo baja lógica para preservar el histórico.

### Reglas de negocio aplicables
- RF-001, RF-002, RF-003, RF-004, RN-09

### Requerimientos relacionados
- RF-001, RF-002, RF-003, RF-004, RNF-011

### Frecuencia / Volumen
- Principalmente a inicio de cada año académico; ajustes ocasionales.

### Notas / Cuestiones abiertas
- Los datos históricos de años anteriores se preservan; las bajas son lógicas.

---

## Matriz de Trazabilidad CU ↔ RF

| Caso de Uso | Requerimientos Funcionales |
|-------------|---------------------------|
| CU-01 | RF-010, RF-011, RF-012, RF-013, RF-014 |
| CU-02 | RF-030, RF-031, RF-053 |
| CU-03 | RF-032, RF-040, RF-041, RF-042, RF-061 |
| CU-04 | RF-033, RF-043, RF-061 |
| CU-05 | RF-034, RF-043, RF-061 |
| CU-06 | RF-020, RF-028 |
| CU-07 | RF-021, RF-004 |
| CU-08 | RF-022, RF-023, RF-024, RF-025, RF-027, RF-060 |
| CU-09 | RF-028, RF-043 |
| CU-10 | RF-024, RF-025, RF-043 |
| CU-11 | RF-050, RF-051, RF-052 |
| CU-12 | RF-035 |
| CU-13 | RF-042, RF-043 |
| CU-14 | RF-026 |
| CU-15 | RF-054 |
| CU-16 | RF-001, RF-002, RF-003, RF-004 |

---

## Notas Generales

1. **Formato de planificaciones**: Todas las planificaciones se manejan como documentos Word (.doc/.docx) según las plantillas institucionales (ICES y UCSE).

2. **Histórico de instancias**: El sistema conserva el histórico completo de todas las instancias de años anteriores, permitiendo consulta y auditoría.

3. **Marca de entrega tardía**: Solo se registra la fecha de entrega y si fue posterior a la fecha límite. No existe un esquema de cumplimientos con categorías o puntajes adicionales.

4. **Versionado**: Cada envío genera una nueva versión; las versiones anteriores (enviadas, rechazadas, reemplazadas) quedan en el histórico.

5. **Doble aprobación**: Toda aprobación final requiere visto de moderadora + coordinador (RN-03).

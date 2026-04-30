# Visión del Producto

## Problema
Hoy las planificaciones docentes (anuales o cuatrimestrales) se gestionan por **mail** y se archivan en **carpetas de Google Drive**. La Secretaría Académica envía periódicamente a los profesores la solicitud de presentación con un mes de plazo, recibe los documentos Word por mail, los revisa junto con los coordinadores y los archiva manualmente. Esto genera:
- Falta de trazabilidad (quién entregó, cuándo, en qué versión).
- Control manual de entregas tardías en planillas Excel.
- Riesgo de pérdida o confusión entre versiones.
- Dificultad para que alumnado, coordinadores y equipo de gestión consulten la versión oficial.

## Propósito
Centralizar la solicitud, envío, revisión y archivo de planificaciones docentes de **ICES** y **UCSE** en una única plataforma, con versionado, control automático de campos obligatorios, registro de la versión oficial y acceso diferenciado por rol.

## Alcance (preliminar — a validar)
**Incluye:**
- Gestión de **instancias de presentación** programables por la secretaría (ej.: marzo — anuales y 1° cuatrimestre; abril — TGO/Desarrollo de Software; julio — 2° cuatrimestre).
- Notificación automática por mail a profesores en grupos por institución (ICES / UCSE).
- Carga de la planificación por el profesor sobre una **plantilla con campos obligatorios** (Word adjunto y/o formulario estructurado).
- **Validación automática de completitud**: si falta algún campo obligatorio, rechazo automático.
- Revisión con **doble aprobación** (moderadora + coordinador correspondiente).
- Reenvío de nuevas versiones por el profesor; historiál completo.
- Marca de **entrega tardía** (sin bloquear el envío).
- Registro de la versión aprobada como **oficial** del período, accesible a alumnado, coordinadores y gestión.
- Modificación de planificación ya aprobada con historiál versión vieja / nueva.

**No incluye (a confirmar):**
- Cálculo del premio por cumplimiento de objetivos del docente (puede sí exponer los datos para ese cálculo).
- Evaluación pedagógica automática del contenido.
- Migración histórica de planificaciones anteriores al sistema (a evaluar).

## Objetivos medibles
- 100% de planificaciones con versión oficial identificable y accesible.
- Reducción del control manual en Excel de entregas tardías a 0.
- Trazabilidad completa: quién entregó/aprobó/rechazó qué y cuándo.
- Tiempo desde el envío del aviso hasta la aprobación: a baseline en primera medición.

## Restricciones conocidas
- Conviven **dos instituciones**: ICES y UCSE (con plantillas potencialmente distintas).
- Periodicidad: **anual** o **cuatrimestral** según la materia (definida a inicio de año por el plan de estudios).
- **Moderadora única** (Secretaría Académica) + coordinadores que aprueban en conjunto.
- Las fechas de cada instancia deben ser **configurables** (no hardcodeadas).
- Hoy el repositorio operativo es Google Drive; evaluar integración o reemplazo.

## Supuestos
- A inicio de año se carga el listado completo de materias con su régimen (anual / 1° cuat / 2° cuat) y profesor titular.
- Cada profesor pertenece a una sola institución a efectos de notificación.
- La versión oficial es **única** por (profesor, materia, período académico).

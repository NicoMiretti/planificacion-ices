# Acta de Reunión — Moderadora (Secretaría Académica)

- **Fecha:** 2026-04-30
- **Entrevistada:** Ari — Secretaría Académica (moderadora única)
- **Entrevistador (analista):** Nicolás
- **Objetivo:** Entender el proceso AS-IS de gestión de planificaciones docentes y necesidades para el sistema TO-BE.

> Esta acta es la fuente primaria del relevamiento. Los hallazgos aquí registrados se reflejan en visión, glosario, requerimientos, reglas de negocio y casos de uso.

## 1. Contexto institucional
- Conviven **dos instituciones** en la operatoria: **ICES** y **UCSE**. Cada profesor pertenece a una (los mails se envían en grupos separados por institución).
- La entrevistada es **moderadora única** del proceso (no hay reparto entre moderadores).
- Reporta los resultados a **coordinadores** y **alumnado**.

## 2. Formato actual de la planificación
- Documento **Word** con plantilla **única para todas las materias**.
- Existen **dos modelos** de plantilla: uno para ICES y otro para UCSE.
- **Componentes obligatorios** (la ausencia de cualquiera de ellos provoca **rechazo automático**):
  1. **Propósito**
  2. **Fundamentación** (contextualización de la propuesta) — *ver grabación para detalle*
  3. **Contenidos mínimos**
  4. **Metodología** (incluye formato)
  5. **Requisitos para regularizar y promocionar**
  6. **Criterios y formatos de evaluación** (instancias evaluativas, meses, formato escrito/oral)
  7. **Bibliografía** (lo más importante)

## 3. Flujo AS-IS
1. **Secretaría** envía un mail a los profesores informando la apertura de la instancia de presentación.
   - Mails separados por institución (ICES y UCSE).
   - El mail incluye link a una **carpeta de Drive** con: modelo de planificación, documento orientador, reglamento (ej. Reglamento ICES 2026), calendario académico.
   - Plazo: **un mes** desde el envío del mail.
2. El **profesor titular** completa la plantilla Word y responde por mail con el documento.
3. Tras la **fecha límite**, los **coordinadores** evalúan junto con la moderadora.
4. **Doble aprobación**: la moderadora y el coordinador correspondiente aprueban (o rechazan).
5. El coordinador reúne todas las planificaciones aprobadas y se las envía a la moderadora.
6. La moderadora las archiva en una **segunda carpeta Drive** (repositorio de planificaciones).

> Hoy operan con **dos carpetas en Drive**:
> - **Carpeta 1**: documentación a enviar a docentes (plantilla, reglamento, calendario, guía APA, etc.).
> - **Carpeta 2**: lista de planificaciones recibidas/oficiales.

## 4. Calendario real (instancias programables)
- **Marzo**: aviso general (anuales y 1° cuatrimestre).
- **Principios de abril**: aviso a TGO y Desarrollo de Software (carreras con cronograma propio).
- **Julio**: aviso para materias del **2° cuatrimestre**, que se entregan en **agosto**.
- **A inicio de año** se conoce el listado completo de materias con su régimen (anual / 1° cuatrimestre / 2° cuatrimestre).
- Las fechas tienen que ser **configurables** y permitir **múltiples instancias** a lo largo del año.

## 5. Revisión y criterios
- Se revisa **formato** y **completitud** (que estén todos los campos obligatorios).
- **Errores leves**: la moderadora puede acomodarlos sin devolver al profesor.
- **Tiempo de revisión**: variable, no medido formalmente.
- **Decisión**: consultada con el coordinador; ambos aprueban o rechazan.
- **Idas y vueltas**: pueden ocurrir; si se vuelve muy lento, moderadora + coordinador pueden **definir y cerrar** sin más rondas.

## 6. Entregas tardías
- **No se bloquean** envíos fuera de fecha.
- Se **marcan** como entrega tardía (hoy se lleva en Excel).
- Más de **10 a 15 días** de atraso se considera mucho.
- Hay un **premio por cumplimiento de objetivos** del docente; entregar en tiempo y forma es uno de los objetivos.

## 7. Modificación de una planificación ya aprobada
- Caso poco frecuente pero contemplado.
- Se hacen **reuniones con el profesor**, se buscan las planificaciones, se **comparan contenidos**.
- Queda **histórico**: versión vieja y versión nueva conviven.
- En materias **anuales** no hay ratificación a mitad de año.

## 8. Roles y permisos identificados
| Rol | Acciones |
|---|---|
| **Moderadora (Ari) + Coordinadores** | Revisan, aprueban, rechazan; ven histórico de rechazos; gestionan modificaciones. |
| **Profesores** | Crean, envían y reenvían sus planificaciones. |
| **Alumnado** | Consulta planificaciones oficiales. |
| **Secretarías generales / Equipo de gestión** | Consultan planificaciones oficiales cuando lo necesitan. |

## 9. Necesidades del sistema TO-BE
- **Pantalla principal** organizada por **Carrera → Año de cursado** (1°, 2°, 3°, …; algunas materias abarcan varios años).
- **Notificaciones**: mail a la secretaría cuando llega una planificación nueva.
- **Marcar (no bloquear)** entregas tardías.
- **Histórico de versiones** completo, incluyendo rechazadas.
- **Acceso al histórico de rechazos**: solo moderadora y coordinador.
- Posibilidad de **clonar** planificación de un período anterior para acelerar la carga (a confirmar en próxima reunión).

## 10. Documentos entregados / referencias
- Mail de ejemplo del Ciclo Lectivo 2026 (ver carpeta `referencia/`).
- Link Drive (compartido por la entrevistada): https://drive.google.com/drive/folders/1wwJjBeKoUi1PqkpTeXjU6uiWnh-yQAOQ
- Materiales en la carpeta: modelo de planificación (ICES y UCSE), documento orientador, Reglamento ICES 2026, calendario académico, guía de normas APA, reglamento interno docente, reglamento interno ISPA.

## 11. Pendientes / dudas para próximas rondas
| # | Pendiente | Responsable |
|---|---|---|
| 1 | Confirmar contenido detallado de "Fundamentación" (revisar grabación). | Analista |
| 2 | Definir si los modelos ICES y UCSE difieren en campos o solo en formato. | Moderadora |
| 3 | Confirmar política exacta de "errores leves" que la moderadora corrige sin devolver (¿se registra?). | Moderadora |
| 4 | Confirmar visibilidad para alumnado (¿solo oficial vigente o también histórico?). | Moderadora + Coordinadores |
| 5 | Definir esquema de "premio por cumplimiento" (¿lo calcula el sistema o solo expone datos?). | Equipo de gestión |
| 6 | Entrevistar a un **coordinador** y a un **profesor**. | Analista |

---
**Validación de la entrevistada:** ☐ Pendiente

# Guía de Usuario — Moderadora
## Sistema de Planificaciones Académicas · ICES / UCSE

**Versión del documento:** 1.0  
**Fecha:** Junio 2026  
**Audiencia:** Secretaría Académica (rol Moderadora)  
**URL del sistema:** http://190.13.88.96/planificaciones/

---

## Índice

1. [Acceso al sistema](#1-acceso-al-sistema)
2. [Panel de inicio](#2-panel-de-inicio)
3. [Ciclo de vida de una convocatoria](#3-ciclo-de-vida-de-una-convocatoria)
4. [Gestión de Instancias de Presentación](#4-gestión-de-instancias-de-presentación)
   - 4.1 [Ver listado de instancias](#41-ver-listado-de-instancias)
   - 4.2 [Crear una nueva instancia](#42-crear-una-nueva-instancia)
   - 4.3 [Ver detalle de una instancia](#43-ver-detalle-de-una-instancia)
   - 4.4 [Editar una instancia](#44-editar-una-instancia)
   - 4.5 [Eliminar una instancia](#45-eliminar-una-instancia)
5. [Circuito de revisión](#5-circuito-de-revisión)
   - 5.1 [Tablero de revisión](#51-tablero-de-revisión)
   - 5.2 [Revisar una planificación](#52-revisar-una-planificación)
   - 5.3 [Dar visto bueno (aprobar)](#53-dar-visto-bueno-aprobar)
   - 5.4 [Rechazar con observaciones](#54-rechazar-con-observaciones)
   - 5.5 [Aplicar corrección leve](#55-aplicar-corrección-leve)
   - 5.6 [Doble aprobación con el Coordinador](#56-doble-aprobación-con-el-coordinador)
6. [Gestión de catálogos](#6-gestión-de-catálogos)
   - 6.1 [Tipos de Planificación](#61-tipos-de-planificación)
   - 6.2 [Carreras](#62-carreras)
   - 6.3 [Materias](#63-materias)
   - 6.4 [Profesores](#64-profesores)
7. [Estados de las planificaciones](#7-estados-de-las-planificaciones)
8. [Escenarios frecuentes](#8-escenarios-frecuentes)
   - 8.1 [Inicio de un nuevo ciclo lectivo](#81-inicio-de-un-nuevo-ciclo-lectivo)
   - 8.2 [Profesor que no cargó su planificación](#82-profesor-que-no-cargó-su-planificación)
   - 8.3 [Planificación con campos obligatorios faltantes](#83-planificación-con-campos-obligatorios-faltantes)
   - 8.4 [El coordinador aún no dio su visto bueno](#84-el-coordinador-aún-no-dio-su-visto-bueno)
   - 8.5 [Corrección de un error tipográfico menor](#85-corrección-de-un-error-tipográfico-menor)
   - 8.6 [Se incorpora un nuevo profesor al plantel](#86-se-incorpora-un-nuevo-profesor-al-plantel)
   - 8.7 [Se cambia el titular de una materia](#87-se-cambia-el-titular-de-una-materia)
9. [Preguntas frecuentes](#9-preguntas-frecuentes)

---

## 1. Acceso al sistema

Ingresar desde cualquier navegador a:

```
http://190.13.88.96/planificaciones/
```

Utilizar las siguientes credenciales:

| Campo | Valor |
|-------|-------|
| Email | ariatna.weishein@ices.edu |
| Contraseña | `Mod@Ices2026` (temporal — se recomienda cambiarla) |

> **Para cambiar la contraseña:** hacer clic en el nombre de usuario en la barra superior → *Mi perfil* → *Cambiar contraseña*. También puede hacerse desde el panel de administración en `/planificaciones/admin/`.

---

## 2. Panel de inicio

Al iniciar sesión, el sistema muestra un **panel de inicio** con un resumen del estado general:

- **Instancias activas:** convocatorias abiertas o programadas en el ciclo actual.
- **Planificaciones pendientes de revisión:** cantidad de documentos esperando revisión.
- **Accesos rápidos:** botones directos al tablero de revisión y a la gestión de instancias.

La barra de navegación superior contiene los accesos a todos los módulos:

| Sección | Descripción |
|---------|-------------|
| **Inicio** | Panel con resumen del estado general |
| **Convocatorias** | Gestión de instancias de presentación |
| **Revisión** | Tablero de planificaciones pendientes de revisión |
| **Catálogos** | ABM de tipos de planificación, carreras, materias y profesores |

---

## 3. Ciclo de vida de una convocatoria

El flujo completo de una convocatoria sigue estas etapas:

```
[Moderadora crea instancia]
         ↓
   Estado: PROGRAMADA
   (antes de la fecha de apertura)
         ↓
   Estado: ABIERTA
   (entre fecha_apertura y fecha_limite)
   → Profesores pueden subir sus planificaciones
         ↓
   [Profesor sube documento Word]
   → El sistema valida los campos obligatorios automáticamente
   → Si pasa: estado planificación = EN REVISIÓN
   → Si falla: estado = RECHAZADA AUTOMÁTICAMENTE (el profesor corrige y reenvía)
         ↓
   [Moderadora y Coordinador revisan]
   → Cualquiera de los dos puede:
       • Dar VISTO BUENO (ambos deben hacerlo para aprobar)
       • RECHAZAR con observaciones (el profesor reenvía una nueva versión)
       • Moderadora puede aplicar CORRECCIÓN LEVE (sin devolver al profesor)
         ↓
   [Cuando AMBOS dan visto bueno]
   → Estado planificación = OFICIAL VIGENTE ✓
         ↓
   [Moderadora cierra la instancia]
   Estado: CERRADA
```

---

## 4. Gestión de Instancias de Presentación

Una **instancia de presentación** es una convocatoria formal que define:
- Qué carreras y años deben presentar planificaciones.
- En qué período del año (anual, 1° o 2° cuatrimestre, o todos).
- Las fechas de apertura y cierre.
- El tipo de planificación requerido (con sus secciones obligatorias).

### 4.1 Ver listado de instancias

**Ruta:** Menú superior → *Convocatorias*

Se muestra una tabla con todas las instancias. Es posible filtrar por:
- **Año académico**
- **Estado** (Programada / Abierta / Cerrada)

Cada fila muestra: nombre, año, período, fechas, estado y acciones disponibles.

### 4.2 Crear una nueva instancia

**Ruta:** Menú superior → *Convocatorias* → botón **Nueva instancia**

El formulario solicita los siguientes campos:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Nombre** | Título descriptivo de la convocatoria | "Planificaciones 1° Cuatrimestre 2026" |
| **Año académico** | Año al que corresponde | 2026 |
| **Período** | Régimen de las materias incluidas | 1° Cuatrimestre |
| **Tipo de planificación** | Define los campos obligatorios del documento Word | "Planificación ICES" |
| **Carreras** | Selección múltiple de carreras incluidas | Tecnicatura en Desarrollo de Software |
| **Años de cursado** | Qué años incluir (1°, 2°, 3°...). Si se deja vacío, incluye todos | 1, 2 |
| **Fecha de apertura** | A partir de cuándo los profesores pueden cargar documentos | 01/03/2026 |
| **Fecha límite** | Fecha hasta la que el envío es considerado en término | 31/03/2026 |

> **Nota:** Los años de cursado disponibles se cargan dinámicamente según las carreras seleccionadas. Al cambiar la selección de carreras, los checkboxes de años se actualizan automáticamente.

Al guardar, el sistema:
1. Crea la instancia en estado **Programada** (o **Abierta** si la fecha de apertura ya pasó).
2. Genera automáticamente una planificación vacía por cada combinación materia–profesor titular dentro de la audiencia definida.

> **Importante:** Si una materia no tiene profesor titular asignado en el catálogo, no se generará planificación para ella. Verificar el catálogo de materias antes de crear la instancia.

### 4.3 Ver detalle de una instancia

**Ruta:** En el listado, hacer clic en el nombre de la instancia o en el ícono de detalle.

La vista de detalle muestra:
- Datos generales de la convocatoria.
- Una tabla con **todas las materias de la audiencia** y el estado de cada planificación.

La tabla incluye columnas de filtro por carrera y año de cursado (visible cuando hay más de una carrera o año).

Los estados posibles en la columna de planificación son:

| Estado visible | Significado |
|----------------|-------------|
| Sin cargar | El profesor aún no subió nada |
| Borrador | Subido pero aún no enviado a revisión |
| En revisión | Aguardando revisión |
| Rechazada | El revisor la rechazó; el profesor debe reenviar |
| Rechazada automáticamente | El sistema la rechazó por campos faltantes |
| Oficial vigente ✓ | Aprobada por ambos revisores |

### 4.4 Editar una instancia

**Ruta:** Detalle de instancia → botón **Editar**

Se pueden modificar todos los campos del formulario original. Al guardar:
- Si se **agregan** carreras o años nuevos, se crean las planificaciones faltantes automáticamente.
- Si se **eliminan** carreras, solo se borran las planificaciones que **no tienen contenido** (sin versiones subidas). Las planificaciones con documentos se conservan.

> **Advertencia:** No se recomienda modificar las fechas de una instancia con planificaciones ya en revisión.

### 4.5 Eliminar una instancia

**Ruta:** Listado de instancias → ícono de eliminar (o desde el detalle)

El sistema muestra un resumen de lo que se eliminará (cantidad de planificaciones, versiones y documentos). Se solicita confirmación explícita antes de proceder.

> **Advertencia:** La eliminación es irreversible. Solo se recomienda eliminar instancias **sin contenido cargado** (creadas por error o duplicadas).

---

## 5. Circuito de revisión

### 5.1 Tablero de revisión

**Ruta:** Menú superior → *Revisión*

El tablero muestra todas las versiones de planificaciones que se encuentran actualmente **en estado "En Revisión"**, es decir, documentos enviados por los profesores que aguardan revisión.

Cada fila muestra:
- Nombre del profesor y la materia.
- Carrera e instancia a la que corresponde.
- Fecha de envío.
- Indicador de **entrega tardía** (si fue enviado después de la fecha límite).
- Si la moderadora ya dio su visto bueno.

**Filtros disponibles:**
- Por **carrera**
- Por **entrega tardía** (ver solo las que llegaron fuera de término)

> Las planificaciones se ordenan por estado y luego por fecha de envío (las más antiguas primero).

### 5.2 Revisar una planificación

**Ruta:** Tablero → hacer clic en la fila de la planificación

La vista de revisión muestra:

1. **Datos del documento:** materia, profesor, carrera, instancia, versión.
2. **Enlace de descarga** del archivo Word para su lectura.
3. **Estado de vistos buenos:** quién ya aprobó (moderadora / coordinador) y quién falta.
4. **Historial completo** de acciones sobre la planificación (envíos, rechazos, correcciones, aprobaciones de versiones anteriores).
5. **Sección de campos faltantes:** si el sistema detectó secciones obligatorias ausentes en el documento al momento del envío, se listan aquí como referencia.
6. **Acciones disponibles** (ver secciones siguientes).

### 5.3 Dar visto bueno (aprobar)

Cuando la planificación es correcta, la moderadora puede dar su **visto bueno** haciendo clic en el botón **"Dar visto bueno"**.

**Regla de negocio — Doble aprobación:**
- La planificación requiere visto bueno de **dos revisores**: la **moderadora** y el **coordinador** de la carrera correspondiente.
- Cuando ambos hayan dado el visto bueno, la planificación pasa automáticamente al estado **Oficial Vigente**.
- Si solo uno ha dado el visto bueno, el estado permanece en **En Revisión** y se muestra quién falta.

> El visto bueno no puede darse dos veces por el mismo revisor en la misma versión. El sistema lo previene.

### 5.4 Rechazar con observaciones

Cuando la planificación presenta problemas que requieren corrección por parte del profesor:

1. Hacer clic en el botón **"Rechazar"** en la vista de revisión.
2. Completar el campo de **observaciones** (obligatorio). Describir claramente qué debe corregir el profesor.
3. Confirmar la acción.

**Consecuencias:**
- La versión pasa al estado **Rechazada**.
- El profesor deberá subir una **nueva versión** del documento, que comenzará el ciclo de revisión desde el inicio.
- Los vistos buenos anteriores sobre esa versión se descartan (aplica a la nueva versión).

> No es posible rechazar una versión que ya fue aprobada (estado Oficial o Aprobada).

### 5.5 Aplicar corrección leve

La corrección leve permite que la moderadora realice una modificación menor al documento **sin devolver la planificación al profesor**. Es exclusiva del rol de moderadora.

**Cuándo usarla:** errores tipográficos, datos de formato, ajustes menores que no afectan el contenido académico.

**Pasos:**
1. En la vista de revisión, localizar la sección **"Corrección leve"**.
2. Completar el campo **"Detalle de la corrección"** (obligatorio). Describir qué se modificó y por qué.
3. Opcionalmente, adjuntar el **archivo Word corregido** (si la corrección implica reemplazar el documento).
4. Hacer clic en **"Aplicar corrección leve"**.

**Consecuencias:**
- Se registra la corrección en el historial de la planificación con el detalle y el usuario que la realizó.
- La versión **permanece en estado En Revisión** (no se rechaza ni se aprueba automáticamente).
- Si se adjuntó un archivo, este queda disponible para descarga en el historial.
- La moderadora puede luego dar su visto bueno sobre la misma versión.

> **No usar** corrección leve para cambios de contenido académico significativos. En esos casos, rechazar la planificación para que el profesor la corrija.

### 5.6 Doble aprobación con el Coordinador

El coordinador de cada carrera tiene acceso al tablero de revisión para **las planificaciones de sus propias carreras**. El proceso de doble aprobación funciona así:

1. Tanto la moderadora como el coordinador pueden revisar la planificación de forma **independiente y en cualquier orden**.
2. Cada uno da su visto bueno por separado.
3. Cuando **ambos** lo han hecho, el sistema marca la planificación como **Oficial Vigente** automáticamente.
4. Si uno rechaza la planificación, **ambos vistos buenos se invalidan** para esa versión (el profesor deberá reenviar una nueva versión).

**Visibilidad de vistos buenos:** en la vista de revisión se muestra siempre el estado de ambos revisores (quién aprobó y quién no).

---

## 6. Gestión de catálogos

**Ruta:** Menú superior → *Catálogos*

La sección de catálogos permite mantener actualizados los datos maestros del sistema. Solo la moderadora (y el administrador) tienen acceso.

### 6.1 Tipos de Planificación

Los tipos de planificación definen **qué secciones son obligatorias** en los documentos Word que presentan los profesores. El sistema valida automáticamente estos campos al momento del envío.

**Atributos:**

| Campo | Descripción |
|-------|-------------|
| Título | Nombre del tipo (ej: "Planificación ICES") |
| Descripción | Descripción interna |
| Secciones obligatorias | Lista de textos que deben aparecer en el documento |
| Link a documentación | URL con guía o plantilla para los profesores |

**Crear un tipo:** *Catálogos → Tipos de Planificación → Nuevo*

**Editar:** Si el tipo está siendo usado en instancias activas, el sistema muestra una advertencia y solicita confirmación antes de guardar. Los cambios en las secciones obligatorias afectan a futuras validaciones.

**Eliminar:** No es posible eliminar un tipo que esté vinculado a una instancia de presentación existente.

### 6.2 Carreras

Gestión del listado de carreras académicas.

**Atributos:**

| Campo | Descripción |
|-------|-------------|
| Nombre | Nombre oficial de la carrera |
| Institución | ICES o UCSE |
| Coordinador | Usuario con rol Coordinador asignado a esta carrera |
| Activo | Si la carrera aparece disponible en nuevas instancias |

> El coordinador asignado a una carrera es quien recibe las planificaciones para revisión en esa carrera.

### 6.3 Materias

Gestión del listado de materias por carrera.

**Atributos:**

| Campo | Descripción |
|-------|-------------|
| Nombre | Nombre de la materia |
| Carrera | Carrera a la que pertenece |
| Año de cursado | Año de la carrera (1° a 5°) |
| Régimen | Anual, 1° Cuatrimestre o 2° Cuatrimestre |
| Profesor titular | Profesor asignado como titular (puede ser vacío) |
| Activo | Si la materia aparece en nuevas convocatorias |

> Si una materia no tiene profesor titular asignado, **no se generará planificación automática** para esa materia cuando se crea una instancia. Asignar el titular antes de crear la convocatoria.

### 6.4 Profesores

Gestión de los perfiles de profesores. Cada profesor está vinculado a un usuario del sistema.

**Atributos:**

| Campo | Descripción |
|-------|-------------|
| Usuario | Cuenta de acceso del profesor (email, contraseña) |
| Institución | Institución a la que pertenece |
| Activo | Si el profesor aparece como titular disponible |

> Para crear un nuevo profesor, primero debe existir un **usuario** con rol `Profesor`. El perfil de profesor se crea a partir de ese usuario.

---

## 7. Estados de las planificaciones

Cada planificación transita por los siguientes estados:

```
BORRADOR
   │
   │ El profesor envía el documento
   ▼
Validación automática de campos obligatorios
   │
   ├─ Campos OK ──────────────────► EN REVISIÓN
   │                                    │
   └─ Campos faltantes ─► RECHAZADA     ├─ Moderadora o coordinador rechaza
                          AUTOMÁTICA    │   → vuelve al profesor (nueva versión)
                            │           │
                     Profesor corrige   ├─ Moderadora da visto bueno
                     y reenvía          │   (falta coordinador) → sigue EN REVISIÓN
                            │           │
                            └──────────►├─ Coordinador da visto bueno
                                        │   (falta moderadora) → sigue EN REVISIÓN
                                        │
                                        └─ AMBOS dan visto bueno → OFICIAL VIGENTE ✓
```

| Estado | Significado |
|--------|-------------|
| **Borrador** | El profesor lo guardó pero no lo envió formalmente |
| **En Revisión** | Esperando revisión de moderadora y coordinador |
| **Rechazada automática** | El sistema detectó secciones obligatorias faltantes |
| **Rechazada** | Un revisor la rechazó con observaciones |
| **Oficial vigente** | Aprobada por ambos revisores — proceso completo |

---

## 8. Escenarios frecuentes

### 8.1 Inicio de un nuevo ciclo lectivo

**Contexto:** Comienza el año académico y se deben convocar a los profesores para que presenten sus planificaciones.

**Pasos:**
1. Verificar que el catálogo de materias esté actualizado: *Catálogos → Materias*. Confirmar que cada materia tiene asignado su profesor titular para el ciclo.
2. Verificar que exista el tipo de planificación correspondiente: *Catálogos → Tipos de Planificación*.
3. Ir a *Convocatorias → Nueva instancia*.
4. Completar el formulario con el nombre, año, período, tipo de planificación, carreras, años de cursado y fechas.
5. Guardar. El sistema crea todas las planificaciones automáticamente.
6. Comunicar a los profesores las fechas de la convocatoria.

### 8.2 Profesor que no cargó su planificación

**Contexto:** La fecha límite pasó y el sistema muestra que un profesor no subió nada.

**Verificación:**
1. Ir al detalle de la instancia (*Convocatorias → [nombre de la instancia]*).
2. Buscar la materia del profesor en cuestión. Si aparece **"Sin cargar"**, no ha subido nada.

**Opciones:**
- Contactar al profesor directamente para que suba el documento. Las entregas posteriores a la fecha límite son aceptadas pero quedan marcadas como **tardías**.
- Si la instancia está cerrada, la planificación queda sin contenido en el historial.

### 8.3 Planificación con campos obligatorios faltantes

**Contexto:** Un profesor subió su documento pero el sistema lo rechazó automáticamente.

**Qué sucedió:** Al enviar, el sistema analizó el documento Word y detectó que faltan una o más secciones listadas como obligatorias en el tipo de planificación.

**Acción de la moderadora:**
- En general, no es necesaria ninguna acción: el profesor recibirá la notificación y deberá corregir y reenviar.
- Para ver los detalles, ir al detalle de la instancia y hacer clic en la planificación rechazada.

**Si la detección es incorrecta** (el documento sí contiene el campo pero el sistema no lo reconoció):
- Revisar *Catálogos → Tipos de Planificación* y verificar que el texto de la sección obligatoria coincida exactamente con lo que figura en el documento (mayúsculas, tildes, puntuación).
- Corregir el tipo si es necesario y pedir al profesor que reenvíe el mismo documento.

### 8.4 El coordinador aún no dio su visto bueno

**Contexto:** La moderadora ya aprobó varias planificaciones pero el coordinador no las ha revisado.

**Verificación:** Tablero de revisión → columna de vistos buenos. Las planificaciones con solo el visto bueno de la moderadora muestran que falta el coordinador.

**Acción:**
- Comunicarse con el coordinador para que acceda al sistema y revise las planificaciones de sus carreras en el tablero de revisión.
- El coordinador accede con sus propias credenciales y visualizará exclusivamente las planificaciones de las carreras que coordina.

> La moderadora **no puede dar el visto bueno en nombre del coordinador**.

### 8.5 Corrección de un error tipográfico menor

**Contexto:** La planificación está en revisión y la moderadora detecta un error tipográfico que no justifica devolvérsela al profesor.

**Pasos:**
1. Descargar el documento Word desde la vista de revisión, corregir el error y guardar el archivo.
2. En la vista de revisión → sección **"Corrección leve"**.
3. Completar el detalle: describir qué se corrigió (ej: *"Corrección tipográfica en ítem 3.2: 'objetivoss' → 'objetivos'"*).
4. Adjuntar el archivo Word corregido.
5. Hacer clic en **"Aplicar corrección leve"**.
6. Dar el visto bueno normalmente.

### 8.6 Se incorpora un nuevo profesor al plantel

**Contexto:** Se suma un nuevo docente y debe poder acceder al sistema.

**Pasos:**
1. Ir al panel de administración: http://190.13.88.96/planificaciones/admin/
2. En *Usuarios → Agregar usuario*, completar: email, contraseña temporal, rol **Profesor**, nombre completo.
3. Guardar el usuario.
4. Ir a *Catálogos → Profesores → Nuevo profesor*.
5. Seleccionar el usuario recién creado e indicar la institución. Guardar.
6. Si el profesor es titular de alguna materia, ir a *Catálogos → Materias* y asignarle las materias correspondientes.

### 8.7 Se cambia el titular de una materia

**Contexto:** Un profesor deja de dictar una materia y es reemplazado por otro.

**Pasos:**
1. Ir a *Catálogos → Materias → [nombre de la materia] → Editar*.
2. Cambiar el campo **Profesor titular** al nuevo docente. Guardar.

**Impacto en convocatorias activas:**
- Las instancias ya abiertas **no se ven afectadas automáticamente**. Las planificaciones existentes quedan asignadas al profesor anterior.
- Si se desea incluir al nuevo profesor en la convocatoria activa, editar la instancia: el sistema creará la planificación para el nuevo titular si no existía.

---

## 9. Preguntas frecuentes

**¿Puedo dar el visto bueno y rechazar al mismo tiempo?**  
No. Son acciones excluyentes. Una vez dado el visto bueno no puede revertirse en la misma versión. Si se detecta un problema después de aprobar, la alternativa es coordinarse con el otro revisor para rechazar, o usar corrección leve si el error es menor.

**¿Qué pasa si rechazo una planificación que el coordinador ya aprobó?**  
El rechazo anula el proceso: la versión pasa a estado Rechazada y el visto bueno del coordinador queda sin efecto. Cuando el profesor suba una nueva versión, ambos revisores deberán volver a aprobarla.

**¿Puedo modificar las fechas de una instancia después de que los profesores empezaron a cargar?**  
Técnicamente sí. Se recomienda hacerlo con precaución y comunicar el cambio a los profesores. Extender la fecha límite solo suma tiempo disponible; no afecta retroactivamente las entregas ya realizadas.

**¿Cómo sé si un documento fue entregado tarde?**  
En el tablero de revisión las entregas tardías están marcadas con un indicador visual. También hay un filtro *"Solo tardías"* disponible en el tablero.

**¿El sistema envía notificaciones por email a los profesores?**  
El módulo de notificaciones está integrado. Las acciones de rechazo y aprobación generan notificaciones internas en el sistema. Consultar con el administrador si el envío de correos electrónicos está configurado.

**¿Puedo ver el historial de una planificación de años anteriores?**  
Sí. Desde el detalle de cualquier instancia (incluso las cerradas) se puede acceder a cada planificación y ver su historial completo de versiones, envíos, rechazos y aprobaciones.

**¿Qué sucede si elimino un tipo de planificación que estaba en uso?**  
El sistema no lo permite. Mostrará un mensaje de error indicando que el tipo está vinculado a instancias existentes.

**¿Pueden haber varias instancias abiertas al mismo tiempo?**  
Sí. Por ejemplo, puede coexistir una instancia para materias anuales y otra para materias del 1° cuatrimestre. Cada una es independiente.

---

*Documento elaborado en base al código fuente del sistema. Versión 1.0 — Junio 2026.*

# Guía de prueba: Flujo completo del sistema

Esta guía describe paso a paso cómo probar el sistema desde cero, incluyendo todas las bifurcaciones posibles del flujo de planificaciones.

---

## Cuentas disponibles tras el reset

| Rol            | Email                           | Contraseña |
|----------------|---------------------------------|------------|
| Admin          | *(superusuario, acceso via /admin/)* | —   |
| Moderadora     | moderadora@ices.edu             | mod123     |
| Coord. Sistemas | coord.sistemas@ices.edu        | coord123   |
| Coord. Administ.| coord.contabilidad@ices.edu    | coord123   |

> Para resetear la base y volver a este estado inicial:
> ```
> docker-compose exec web python manage.py seed_data --reset
> ```

---

## Fase 1 — Setup del catálogo (Moderadora)

> Todas las acciones de esta fase son en **Catálogo** (menú superior).
> El orden correcto es: Institución → Carrera → Profesores → Materias.

### 1.1 Crear una institución

**Catálogo → Instituciones → Nueva Institución**

- Nombre: `Instituto de Ciencias y Estudios Superiores`
- Código: `ICES` *(código corto único, se usa en badges y filtros)*

### 1.2 Crear una carrera

**Catálogo → Carreras → Nueva Carrera**

- Nombre: `Ingeniería en Sistemas`
- Institución: `ICES`
- Coordinador: `Carlos Rodríguez` *(coord.sistemas)*
- Activa: ✓

### 1.3 Crear profesores

**Catálogo → Profesores → Nuevo Profesor**

Crear al menos dos:

| Nombre          | Email              | Contraseña | Institución | Legajo |
|-----------------|--------------------|------------|-------------|--------|
| Roberto Pérez   | perez@ices.edu     | prof123    | ICES        | P-001  |
| Claudia Gómez   | gomez@ices.edu     | prof123    | ICES        | P-002  |

> ⚠️ El formulario crea el usuario y el perfil de profesor en un solo paso.

### 1.4 Crear materias

**Catálogo → Materias → Nueva Materia**

Crear al menos estas dos:

| Nombre           | Carrera               | Año | Régimen | Titular        |
|------------------|-----------------------|-----|---------|----------------|
| Programación I   | Ingeniería en Sistemas| 1   | Anual   | Roberto Pérez  |
| Base de Datos    | Ingeniería en Sistemas| 2   | 1° Cuat | Claudia Gómez  |

> ⚠️ **Regla de negocio:** Una materia sin titular no generará planificación al crear la instancia. Si todas las materias de una carrera/régimen carecen de titular, el sistema **no permitirá crear la instancia** (validación en el formulario).

---

## Fase 2 — Crear instancia de presentación (Moderadora)

**Instancias → Nueva Instancia**

### Campos del formulario

| Campo | Descripción |
|-------|-------------|
| Nombre | Ej: `Anuales 2026` |
| Año académico | `2026` |
| Período | `Anual` / `1° Cuatrimestre` / `2° Cuatrimestre` |
| Fecha apertura | Desde cuando los profesores pueden cargar |
| Fecha límite | Hasta cuando pueden enviar (después es entrega tardía) |
| Carreras | Seleccionar una o varias carreras |
| Filtrar por régimen | Ver opciones abajo |

### Opción "Filtrar materias por régimen"

| Opción | Qué incluye |
|--------|-------------|
| *(usar el período)* | Solo materias cuyo régimen coincide con el período (recomendado) |
| `Todos los regímenes` | Todas las materias activas de las carreras seleccionadas |
| `Anual` / `1° Cuat` / `2° Cuat` | Forzar un régimen específico |

> Al guardar, el sistema **auto-crea una planificación** por cada materia con titular en la combinación carrera + régimen. Si no hay ninguna → **error de validación, no se crea la instancia**.

### Estados de la instancia

```
programada → abierta → cerrada
```

- **Programada**: fecha_apertura futura, los profesores no ven la instancia aún
- **Abierta**: entre fecha_apertura y fecha_límite (o después si se mantuvo abierta)
- **Cerrada**: manualmente por la moderadora o vencida

---

## Fase 3 — Carga de planificación (Profesor)

**Mis Instancias → [instancia] → Cargar**

El profesor ve solo las instancias donde tiene materias asignadas.

### 3.1 Subir borrador

- Hacer clic en **Cargar** junto a su materia
- Subir un archivo `.docx`
- El sistema valida que el documento contenga los 7 campos obligatorios:
  1. Propósito
  2. Fundamentación
  3. Contenidos Mínimos
  4. Metodología
  5. Requisitos para regularizar y promocionar
  6. Criterios y formatos de evaluación
  7. Bibliografía

### Bifurcación A — Rechazo automático (documento incompleto)

Si faltan campos obligatorios:

```
[Borrador] → ENVIAR → [Rechazada automáticamente]
```

- El profesor ve qué campos faltan
- Puede subir una **nueva versión** (v2, v3, …)
- Cada versión queda registrada en el historial

### Bifurcación B — Envío exitoso

```
[Borrador] → ENVIAR → [Enviada]
```

- Si la fecha de entrega superó el `fecha_limite` → se marca como **entrega tardía** con días de atraso
- El profesor **no puede editar** la versión una vez enviada

---

## Fase 4 — Revisión (Moderadora)

**Tablero → [versión enviada] → Tomar revisión**

```
[Enviada] → TOMAR REVISIÓN → [En revisión]
```

Una vez tomada, la moderadora tiene dos opciones:

### Bifurcación C — Aprobación

```
[En revisión] → APROBAR → [Aprobada]
```

El sistema requiere **doble visto bueno** (moderadora + coordinador de la carrera) para marcar como Oficial.

- La moderadora da su visto bueno
- El coordinador de la carrera también debe dar el visto bueno (desde la misma pantalla de detalle)
- Cuando ambos vistos están registrados: versión pasa a **Oficial vigente**

```
[Aprobada] → VB Moderadora + VB Coordinador → [Oficial vigente]
```

### Bifurcación D — Rechazo con observaciones

```
[En revisión] → RECHAZAR → [Rechazada]
```

- La moderadora escribe observaciones explicando el motivo
- El profesor recibe el rechazo y puede ver las observaciones
- El profesor sube una **nueva versión** desde el detalle de la planificación

```
[Rechazada] → Profesor sube v2 → [Borrador v2] → ENVIAR → [Enviada v2] → ...
```

---

## Fase 5 — Actualización (nueva versión oficial)

Si en una instancia posterior se aprueba una nueva versión de la misma materia:

```
[Oficial vigente v1] → [Reemplazada]
[Oficial vigente v2] ← nueva oficial
```

El historial de versiones siempre se conserva.

---

## Diagrama de estados completo (Version)

```
                    ┌──────────────────────────────────────────────────┐
                    │                                                  │
              ┌─────▼─────┐                                           │
         ─────►  Borrador  │                                           │
              └─────┬─────┘                                           │
                    │ ENVIAR                                           │
           ┌────────┴────────┐                                         │
           │                 │                                         │
    Doc incompleto     Doc completo                                    │
           │                 │                                         │
    ┌──────▼──────┐   ┌──────▼──────┐                                 │
    │  Rechazada  │   │   Enviada   │                                 │
    │ (automático)│   └──────┬──────┘                                 │
    └──────┬──────┘          │ TOMAR REVISIÓN                          │
           │          ┌──────▼──────┐                                 │
     Nueva versión    │ En revisión │                                 │
           │          └──────┬──────┘                                 │
           │       ┌─────────┴─────────┐                              │
           │   RECHAZAR           APROBAR                             │
           │       │                   │                              │
           │ ┌─────▼─────┐     ┌───────▼──────┐                      │
           │ │ Rechazada │     │   Aprobada   │                      │
           │ └─────┬─────┘     └───────┬──────┘                      │
           │       │                   │ VB Mod + VB Coord            │
     Nueva versión │            ┌──────▼──────┐                      │
           │       │            │   Oficial   ├──────────────────────┘
           └───────┘            │   vigente   │ (nueva versión aprobada
                                └──────┬──────┘  en instancia futura)
                                       │
                                ┌──────▼──────┐
                                │ Reemplazada │
                                └─────────────┘
```

---

## Casos de prueba sugeridos

### Caso 1 — Flujo feliz completo
1. Setup completo (institución, carrera, profesor, materia con titular)
2. Crear instancia anual abierta
3. Loguearse como profesor → cargar planificación completa → enviar
4. Loguearse como moderadora → tomar revisión → aprobar
5. Dar visto bueno de moderadora
6. Loguearse como coordinador → dar visto bueno
7. Verificar que la versión queda en **Oficial vigente**

### Caso 2 — Rechazo automático por documento incompleto
1. Profesor sube un `.docx` sin los 7 campos
2. Al enviar → estado pasa a **Rechazada automáticamente**
3. El sistema muestra qué campos faltan
4. Profesor sube v2 correcta → repite el flujo feliz

### Caso 3 — Rechazo con observaciones
1. Profesor sube y envía una versión
2. Moderadora toma revisión → rechaza con comentario
3. Profesor ve el rechazo y las observaciones
4. Sube v2 → ciclo completo

### Caso 4 — Entrega tardía
1. Crear instancia con `fecha_límite` = ayer
2. Profesor carga y envía
3. Verificar que la versión queda marcada como **entrega tardía** con días de atraso

### Caso 5 — Instancia sin profesores (validación)
1. Crear materia SIN profesor titular
2. Intentar crear instancia solo con esa carrera/régimen
3. El formulario debe mostrar error y no crear la instancia

### Caso 6 — Múltiples versiones / nueva instancia
1. Año 2025: planificación de Prog I llega a Oficial
2. Año 2026: se crea nueva instancia
3. Profesor carga nueva versión de Prog I
4. Al aprobar: la v1 pasa a **Reemplazada**, la nueva queda como **Oficial vigente**

### Caso 7 — Cambio de titular entre años
1. Materia tenía a Pérez como titular en 2025 → planificación oficial
2. Cambiar el titular de la materia a Gómez
3. Crear instancia 2026
4. Pérez sigue viendo su historial 2025 en "Mis Instancias"
5. Gómez ve la instancia 2026 y tiene que cargar su planificación

---

## Roles y permisos resumidos

| Acción | Moderadora | Coordinador | Profesor | Alumno |
|--------|:----------:|:-----------:|:--------:|:------:|
| Gestionar catálogo (ABM) | ✓ | — | — | — |
| Crear instancias | ✓ | — | — | — |
| Ver todas las instancias | ✓ | ✓ | — | — |
| Ver sus instancias | — | — | ✓ | — |
| Cargar planificación | — | — | ✓ | — |
| Tomar revisión / aprobar / rechazar | ✓ | — | — | — |
| Dar visto bueno | ✓ | ✓ | — | — |
| Consulta pública (planifs oficiales) | ✓ | ✓ | ✓ | ✓ |

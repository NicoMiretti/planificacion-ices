# Guía de prueba: Flujo completo del sistema

Esta guía describe paso a paso cómo probar el sistema desde cero, incluyendo todas las bifurcaciones posibles del flujo de planificaciones.

---

## Cuentas disponibles tras el reset

| Rol        | Email                | Contraseña |
|------------|----------------------|------------|
| Admin      | *(superusuario, acceso via /admin/)* | — |
| Moderadora | moderadora@ices.edu  | mod123     |

> Los coordinadores **no se crean** en el reset. La moderadora los da de alta desde el Catálogo (paso 1.1).

### Comandos de seed disponibles

| Comando | Qué deja |
|---------|----------|
| `seed_data --reset` | Solo moderadora (base vacía, sin catálogo) |
| `seed_data --catalogo` | Moderadora + 2 coordinadores + 2 carreras + 4 profesores + 15 materias. **Las instancias las creás vos.** |
| `seed_data` | Dataset completo de prueba (instancias 2024–2026 + planificaciones en distintos estados) |

```bash
docker-compose exec web python manage.py seed_data --reset
docker-compose exec web python manage.py seed_data --catalogo
docker-compose exec web python manage.py seed_data
```

> Con `--catalogo` las cuentas adicionales son:
>
> | Rol | Email | Contraseña |
> |-----|-------|------------|
> | Coordinador | coord.sistemas@ices.edu | coord123 |
> | Coordinador | coord.contabilidad@ices.edu | coord123 |
> | Profesor | perez@ices.edu | prof123 |
> | Profesor | gomez@ices.edu | prof123 |
> | Profesor | silva@ices.edu | prof123 |
> | Profesor | torres@ices.edu | prof123 |

---

## Fase 1 — Setup del catálogo (Moderadora)

> Todas las acciones de esta fase son en **Catálogo** (menú superior).
> El orden correcto es: Coordinadores → Institución → Carrera → Profesores → Materias.

### 1.1 Crear coordinadores

**Catálogo → Coordinadores → Nuevo Coordinador**

Crear al menos uno por carrera:

| Nombre              | Email                        | Contraseña |
|---------------------|------------------------------|------------|
| Carlos Rodríguez    | coord.sistemas@ices.edu      | coord123   |
| Laura Martínez      | coord.contabilidad@ices.edu  | coord123   |

> El formulario crea el usuario con rol `coordinador` en un solo paso. Los coordinadores quedan disponibles para asignar a carreras.

### 1.2 Crear una institución

**Catálogo → Instituciones → Nueva Institución**

- Nombre: `Instituto Cooperativo de Enseñanza Superior`
- Código: `ICES` *(código corto único, se usa en badges y filtros)*

### 1.3 Crear una carrera

**Catálogo → Carreras → Nueva Carrera**

- Nombre: `Ingeniería en Sistemas`
- Institución: `ICES`
- Coordinador: `Carlos Rodríguez` *(coord.sistemas)*
- Activa: ✓

### 1.4 Crear profesores

**Catálogo → Profesores → Nuevo Profesor**

Crear al menos dos:

| Nombre          | Email              | Contraseña | Institución | Legajo |
|-----------------|--------------------|------------|-------------|--------|
| Roberto Pérez   | perez@ices.edu     | prof123    | ICES        | P-001  |
| Claudia Gómez   | gomez@ices.edu     | prof123    | ICES        | P-002  |

> ⚠️ El formulario crea el usuario y el perfil de profesor en un solo paso.

### 1.5 Crear materias

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
[Borrador] → ENVIAR → [En Revisión]
```

- Al enviar, la versión pasa **directamente** a `En Revisión` (no hay estado intermedio "Enviada")
- Si la fecha de entrega superó el `fecha_limite` → se marca como **entrega tardía** con días de atraso
- El profesor **no puede editar** la versión una vez enviada

---

## Fase 4 — Revisión (Moderadora / Coordinador)

**Tablero → [versión] → Revisar**

El tablero muestra un botón **Revisar** para cualquier versión donde el revisor todavía no dio el visto bueno. El botón **Ver** aparece cuando el revisor ya registró su aprobación.

Las versiones aparecen en el tablero en estado `En Revisión` (no hay estado previo "Enviada" — el envío las deja directamente en revisión).

Una vez en revisión, el revisor tiene dos opciones:

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
[Rechazada] → Profesor sube v2 → [Borrador v2] → ENVIAR → [En Revisión v2] → ...
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
              ┌────────────────────────────────────────────┐
              │                                            │
        ┌─────▼─────┐                                      │
   ─────►  Borrador  │                                      │
        └─────┬─────┘                                      │
              │ ENVIAR                                      │
     ┌────────┴────────┐                                    │
     │                 │                                    │
Doc incompleto    Doc completo                              │
     │                 │                                    │
┌────▼────────┐  ┌──────▼──────┐                           │
│  Rechazada  │  │ En revisión │                           │
│ (automático)│  └──────┬──────┘                           │
└────┬────────┘         │                                   │
     │         ┌────────┴────────┐                          │
     │     RECHAZAR          APROBAR                        │
     │         │                 │                          │
     │  ┌──────▼──────┐  ┌───────▼──────┐                  │
     │  │  Rechazada  │  │   Aprobada   │                  │
     │  └──────┬──────┘  └───────┬──────┘                  │
     │         │                 │ VB Mod + VB Coord        │
Nueva versión  │          ┌──────▼──────┐                  │
     │         │          │   Oficial   ├──────────────────┘
     └─────────┘          │   vigente   │ (nueva versión aprobada
                          └──────┬──────┘  en instancia futura)
                                 │
                          ┌──────▼──────┐
                          │ Reemplazada │
                          └─────────────┘
```

**Estados (7):** `borrador` → `en_revision` → `aprobada` → `oficial` → `reemplazada`
Desde `borrador` también: `rechazada_auto` (doc incompleto)
Desde `en_revision` también: `rechazada` (revisor rechaza con observaciones)

> El estado `enviada` fue eliminado — al enviar el doc pasa directamente a `en_revision`.

---

## Casos de prueba sugeridos

### Caso 1 — Flujo feliz completo
1. Setup: `seed_data --catalogo` (o crear manualmente catálogo e instancia)
2. Crear instancia anual abierta
3. Loguearse como profesor → cargar planificación completa → enviar
4. Loguearse como moderadora → Tablero → **Revisar** → Aprobar
5. Loguearse como coordinador → Tablero → **Revisar** → Aprobar
6. Verificar que la versión queda en **Oficial vigente**

### Caso 2 — Rechazo automático por documento incompleto
1. Profesor sube un `.docx` sin los 7 campos
2. Al enviar → estado pasa a **Rechazada automáticamente**
3. El sistema muestra qué campos faltan
4. Profesor sube v2 correcta → repite el flujo feliz

### Caso 3 — Rechazo con observaciones
1. Profesor sube y envía una versión (queda directamente en revisión)
2. Moderadora → Tablero → **Revisar** → rechaza con comentario
3. Profesor ve el rechazo y las observaciones
4. Sube v2 → ciclo completo

### Caso 4 — Entrega tardía
1. Crear instancia con `fecha_límite` = ayer
2. Profesor carga y envía
3. Verificar que la versión queda marcada como **entrega tardía** con días de atraso (estado: En Revisión)

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
| Revisar (aprobar / rechazar) | ✓ | — | — | — |
| Dar visto bueno | ✓ | ✓ | — | — |

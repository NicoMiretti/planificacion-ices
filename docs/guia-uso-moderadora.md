# Guía de Uso: Sistema de Planificación ICES

Esta guía está diseñada para la **moderadora** y describe todos los flujos posibles del sistema, con puntos de observación para detectar mejoras.

---

## Setup Inicial

### 1. Cargar datos de prueba

```bash
cd src
docker-compose exec web python manage.py seed_data --catalogo
```

**Qué se crea:**
- 1 moderadora: `moderadora@ices.edu` / `mod123`
- 2 coordinadores de carrera
- 2 carreras (Sistemas e Información)
- 15 materias con profesores titulares asignados
- **Sin instancias ni planificaciones** (se crean al hacer la instancia)

### 2. Acceder como moderadora

```
URL: http://localhost:8000
Email: moderadora@ices.edu
Contraseña: mod123
```

---

## Flujo Principal: Camino Feliz

### Fase 1: Moderadora crea Instancia

1. Desde el home → **Instancias → + Nueva Instancia**
2. Completar:
   - **Nombre**: "Anuales 2026" (o similar)
   - **Año académico**: 2026
   - **Período**: "Anual" (o Cuatrimestre)
   - **Fecha apertura**: hoy
   - **Fecha límite**: 30 días de ahora
   - **Carreras**: Seleccionar ambas (Sistemas e Información)
3. **Crear Instancia**

**Observación esperada:**
- Se crea la instancia
- Se auto-crean planificaciones vacías (una por materia + carrera + profesor)
- Redirige al detalle de la instancia
- Muestra todas las materias con profesores titulares

**Puntos a observar:**
- ¿Los nombres de carreras/materias son claros?
- ¿El resumen inicial es útil (cuántas planificaciones hay)?
- ¿Las fechas se muestran en formato correcto?

---

### Fase 2: Profesores cargan versiones

1. Ir a **Instancias → [nombre instancia creada]**
2. **Como profesor 1** (perez@ices.edu / prof123):
   - Home → Mis Instancias → [instancia]
   - Ver la materia asignada
   - **Cargar primera versión** → sube un .docx de prueba
   - Verifica estado: `Borrador`
   - **Enviar** → cambiar a estado `En Revisión`

**Observación esperada:**
- El estado cambia de `Borrador` → `En Revisión`
- La planificación desaparece de "Mis Instancias" (está en revisión)
- Aparece en tablero de revisores como "Revisar"

**Puntos a observar:**
- ¿El flujo de carga es intuitivo?
- ¿Se entiende la diferencia entre Borrador y Enviar?
- ¿El mensaje de confirmación es claro?

---

### Fase 3: Doble visto bueno (Moderadora + Coordinador)

El sistema requiere que **tanto la moderadora como el coordinador de la carrera** aprueben la versión.

**Como moderadora:**
1. **Revisiones → Tablero**
2. Click en **Revisar**
3. **Aprobar** → registra el visto bueno de la moderadora

**Como coordinador** (coord.sistemas@ices.edu / coord123):
1. **Revisiones → Tablero**
2. Click en **Revisar** (o **Ver** si la moderadora ya aprobó)
3. **Aprobar** → registra el visto bueno del coordinador

**Observación esperada:**
- Cuando ambos dieron visto bueno, el estado cambia automáticamente a `Oficial`
- No hay botón manual de "Marcar Oficial" — el sistema lo hace solo al completarse el doble VB
- La planificación desaparece del tablero

**Puntos a observar:**
- ¿Es claro que se necesitan dos aprobaciones?
- ¿El estado intermedio (solo un VB) es visible?

---

## Bifurcaciones y Casos Especiales

### Caso A: Profesor envía después de fecha límite

1. Crear instancia con `fecha_limite` = ayer
2. Profesor carga un .docx y **Envía**
3. El sistema permite el envío pero lo marca como **entrega tardía**

**Observación esperada:**
- El envío no está bloqueado por la fecha límite
- La versión queda en `En Revisión` con indicación de entrega tardía (días de atraso)

**Puntos a observar:**
- ¿Se muestra cuántos días tarde fue la entrega?
- ¿Está claro en el tablero que es una entrega tardía?

---

### Caso B: Revisor rechaza

**Fase 3b:**
1. En el tablero: **Revisar**
2. Cargar comentario en "Razón del rechazo"
3. **Rechazar** → estado `Rechazada`

**Observación esperada:**
- Panel de aprobación cambia a rojo
- Muestra: "El proceso de aprobación se reiniciará cuando el profesor envíe una nueva versión"
- Profesor ve la planificación como `Rechazada` en Mis Instancias

**Puntos a observar:**
- ¿El profesor entiende que puede reenviar?
- ¿El mensaje de rechazo es accesible?

---

### Caso C: Profesor reenvía después de rechazo

**Fase 2c:**
1. Profesor ve planificación rechazada
2. **Cargar nueva versión** (crea nueva versión en `Borrador`)
3. Edita y **Enviar** → nuevo estado `En Revisión`
4. Vuelve al tablero de revisores
5. Revisor **Aprobar** → `Aprobada`

**Observación esperada:**
- El historial de versiones se mantiene
- Solo la última versión se muestra activa
- Los números de versión aumentan (v1, v2, etc.)

**Puntos a observar:**
- ¿Es obvio que puede reenviar?
- ¿Ve claramente qué versión está siendo revisada?

---

### Caso D: Corrección leve (Moderadora)

> Solo la **moderadora** puede aplicar correcciones leves (no el coordinador).

1. En el tablero: **Revisar**
2. Completar el campo de detalle con la corrección aplicada
3. **Aplicar corrección leve** → registra la nota en el historial

**Observación esperada:**
- La versión **permanece en `En Revisión`** (no vuelve a Borrador)
- El historial muestra la corrección aplicada
- El coordinador puede continuar revisando la misma versión

**Puntos a observar:**
- ¿Es claro que la versión sigue en revisión?
- ¿Se diferencia visualmente de un rechazo?

---

### Caso E: Profesor intenta crear instancia sin profesores

**Bifurcación en Fase 1:**
1. Ir a **Instancias → + Nueva Instancia**
2. Seleccionar una carrera que tenga materias sin profesor
3. **Crear Instancia**

**Observación esperada:**
- Error: lista las materias sin profesor
- Bloquea la creación hasta que todos tengan profesor

**Puntos a observar:**
- ¿El mensaje de error es claro?
- ¿Se entiende la razón del bloqueo?

---

### Caso F: Rechazada automáticamente (por validación)

**Nota:** Este caso ocurre internamente si hay datos inconsistentes. En el flujo normal no debería ocurrir si el seed está correcto.

**Observación esperada:**
- Estado `Rechazada automáticamente`
- Mensaje: "El sistema detectó un problema..."

---

## Estadísticas y Vistas

### Instancia - Vista de detalle

En **Instancias → [instancia]**, observar:

| Métrica | Observación |
|---|---|
| **Pendientes** | Planificaciones en `Borrador` (profesor aún edita) |
| **En Revisión** | Esperando revisor |
| **Aprobadas** | Listas para oficializar |
| **Rechazadas** | Esperan reenvío del profesor |

**Puntos a observar:**
- ¿Las categorizaciones son claras?
- ¿Faltan estados intermedios?
- ¿Sería útil filtrar por carrera/profesor?

### Tablero de Revisión

En **Revisiones → Tablero**, observar:

| Columna | Observación |
|---|---|
| **Materia** | Nombre completo visible? |
| **Carrera** | Se sabe de qué carrera es? |
| **Profesor** | Quién es el titular |
| **Instancia** | En cuál período |
| **Estado** | Solo `En Revisión` (no hay otras) |
| **Visto Bueno** | ¿Quién ya vio? |
| **Acciones** | Revisar → lleva al detalle |

**Puntos a observar:**
- ¿Falta información importante?
- ¿Hay demasiadas columnas?
- ¿El botón Revisar es obvio?

---

## Casos Límite para Probar

### 1. Profesor sin instancias asignadas
- Login como profesor con materia no en instancias
- Esperado: "Sin instancias disponibles"

### 2. Cambiar entre instancias
- Profesor carga v1 en instancia A, v1 en instancia B
- Esperado: ambas son independientes (diferentes historiales)

### 3. Revisor sin permisos
- Login como revisor diferente (otro usuario)
- Intentar revisar → ¿ve todas o solo su región/carrera?

### 4. Coordinador ve sus instancias
- Coordinador login
- Esperado: ¿ve las instancias de sus carreras?

### 5. Profesor intenta acceder a instancia cerrada
- Después de fecha límite
- Intenta cargar versión → debe bloquearse
- Intenta enviar borrador → ¿sigue permitido?

---

## Flujo Completo (Walkthrough Recomendado)

**Tiempo: ~15 minutos**

1. ✅ Seed data
2. ✅ Login como moderadora
3. ✅ Crear instancia "TEST 2026"
4. ✅ Login como profesor 1 (perez@)
   - Cargar versión 1
   - Enviar
5. ✅ Login como revisor (moderadora en rol revisor)
   - Revisar tablero
   - Aprobar
6. ✅ Login como profesor 2 (gomez@)
   - Cargar versión 1
   - Enviar
7. ✅ Login como revisor
   - Rechazar con comentario
8. ✅ Login como profesor 2
   - Ver rechazo
   - Cargar versión 2
   - Enviar
8. ✅ Login como revisor (moderadora)
    - Aprobar v2 (primer VB)
9. ✅ Login como coordinador
    - Aprobar v2 (segundo VB) → pasa automáticamente a Oficial
10. ✅ Login como moderadora
    - Ver instancia → verificar estado Oficial

---

## Puntos de Mejora Observados

A medida que uses el sistema, completa esta tabla:

| Punto | Sección | Descripción | Impacto | Estado |
|---|---|---|---|---|
| Ej: Botón pequeño | Tablero | El botón "Revisar" es muy pequeño | Medium | [ ] TODO |
| | | | | |
| | | | | |

---

## Credenciales de Test (post-seed --catalogo)

| Rol | Email | Contraseña | Institución |
|---|---|---|---|
| Moderadora | moderadora@ices.edu | mod123 | ICES |
| Coordinador 1 | coord.sistemas@ices.edu | coord123 | Sistemas |
| Coordinador 2 | coord.contabilidad@ices.edu | coord123 | Contabilidad |
| Profesor 1 | perez@ices.edu | prof123 | Varios |
| Profesor 2 | gomez@ices.edu | prof123 | Varios |
| Profesor 3 | silva@ices.edu | prof123 | Varios |
| Profesor 4 | torres@ices.edu | prof123 | Varios |

---

## Troubleshooting

### "No hay materias con profesor titular asignado"
- El seed no corrió bien, o no seleccionaste carreras con profesores
- Solución: Vuelve a cargar datos con `seed_data --reset` y `--catalogo`

### "La instancia ha cerrado"
- La fecha límite pasó
- Solución: Crea una nueva con fecha futura

### "El proceso de aprobación se reiniciará..."
- La planificación fue rechazada
- Solución: Profesor carga nueva versión

### Planificación desaparece después de enviar
- Está en estado `En Revisión`, no es error
- Es esperado: sale del listado "Mis Instancias" hasta que se resuelva

---

## Notas para el Equipo

- **Estado Oficial**: se asigna automáticamente cuando moderadora + coordinador aprueban (no hay botón manual)
- **Correcciones leves**: vuelven a Borrador (no crean nueva versión oficial)
- **Rechazo automático**: debería no ocurrir (es fallback de seguridad)
- **Media files**: en Render plan Free se pierden, usar S3 para producción

---

**Última actualización**: May 12, 2026  
**Versión del sistema**: Post-refactor (estado `enviada` eliminado)

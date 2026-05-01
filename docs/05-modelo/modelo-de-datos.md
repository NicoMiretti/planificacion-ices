# Modelo de Datos — Sistema de Planificaciones ICES/UCSE

> Diagrama de entidades y relaciones del sistema.  
> Última actualización: Fase 4 completa.

---

## Diagrama ER

```mermaid
erDiagram

    %% =================== USUARIOS ===================
    Usuario {
        int id PK
        string email UK
        string rol
        string nombre_completo
        bool is_active
    }

    %% =================== CATÁLOGOS ===================
    Institucion {
        int id PK
        string nombre
        string codigo UK
        bool activo
    }

    Carrera {
        int id PK
        string nombre
        int institucion_id FK
        int coordinador_id FK
        bool activo
    }

    Profesor {
        int id PK
        int usuario_id FK
        int institucion_id FK
        string legajo
        bool activo
    }

    Materia {
        int id PK
        string nombre
        int carrera_id FK
        int anio_cursado
        string regimen
        int profesor_titular_id FK
        bool activo
    }

    Plantilla {
        int id PK
        int institucion_id FK
        string archivo
        bool activo
        datetime fecha_creacion
    }

    MaterialApoyo {
        int id PK
        string tipo
        int anio_academico
        int institucion_id FK
        string archivo
        bool activo
    }

    %% =================== INSTANCIAS ===================
    InstanciaPresentacion {
        int id PK
        string nombre
        int anio_academico
        string periodo
        int institucion_id FK
        string solo_regimen
        date fecha_apertura
        date fecha_limite
        string estado
        int creada_por_id FK
        datetime fecha_creacion
    }

    InstanciaCarrera {
        int instancia_id FK
        int carrera_id FK
    }

    %% =================== PLANIFICACIONES ===================
    Planificacion {
        int id PK
        int materia_id FK
        int profesor_id FK
        int instancia_id FK
        int version_oficial_id FK
        datetime fecha_creacion
    }

    Version {
        int id PK
        int planificacion_id FK
        int numero
        string archivo
        string estado
        bool entrega_tardia
        int dias_atraso
        json campos_faltantes
        datetime fecha_creacion
        datetime fecha_envio
        datetime fecha_aprobacion
    }

    %% =================== RELACIONES ===================

    %% Catálogos
    Institucion ||--o{ Carrera : "tiene"
    Institucion ||--o{ Profesor : "pertenece"
    Institucion ||--o{ Plantilla : "usa"
    Institucion ||--o{ MaterialApoyo : "publica"
    Usuario ||--o| Profesor : "es"
    Usuario ||--o{ Carrera : "coordina"
    Carrera ||--o{ Materia : "contiene"
    Profesor ||--o{ Materia : "dicta"

    %% Instancias
    InstanciaPresentacion ||--o{ InstanciaCarrera : ""
    Carrera ||--o{ InstanciaCarrera : ""
    Institucion |o--o{ InstanciaPresentacion : "filtra"
    Usuario ||--o{ InstanciaPresentacion : "crea"

    %% Planificaciones
    Materia ||--o{ Planificacion : "tiene"
    Profesor ||--o{ Planificacion : "presenta"
    InstanciaPresentacion ||--o{ Planificacion : "agrupa"
    Planificacion ||--o{ Version : "versiona"
    Version |o--|| Planificacion : "es oficial de"
```

---

## Descripción de Entidades

### Módulo Usuarios

| Entidad | Descripción | Roles |
|---------|-------------|-------|
| `Usuario` | Usuario del sistema con autenticación por email | admin, moderadora, coordinador, profesor, alumno, gestion |

### Módulo Catálogos

| Entidad | Descripción | Notas |
|---------|-------------|-------|
| `Institucion` | ICES o UCSE | Código único (ej: `ICES`) |
| `Carrera` | Carrera académica de una institución | Tiene coordinador (FK a Usuario) |
| `Profesor` | Perfil de un usuario con rol `profesor` | OneToOne con Usuario |
| `Materia` | Materia de una carrera con año, régimen y titular | Régimen: anual, 1cuat, 2cuat |
| `Plantilla` | Archivo Word modelo para planificaciones | Una vigente por institución |
| `MaterialApoyo` | Reglamento, calendario u otros documentos | Por institución y año académico |

### Módulo Instancias

| Entidad | Descripción | Notas |
|---------|-------------|-------|
| `InstanciaPresentacion` | Convocatoria para presentar planificaciones | Estados: programada, abierta, cerrada |
| `InstanciaCarrera` | Tabla pivot M2M instancia ↔ carrera | Define la audiencia |

### Módulo Planificaciones

| Entidad | Descripción | Notas |
|---------|-------------|-------|
| `Planificacion` | Agrupa todas las versiones de una materia en una instancia | Única por (materia, profesor, instancia) |
| `Version` | Archivo Word específico con su estado FSM | Versionado correlativo: v1, v2, … |

---

## Estados de una Versión (FSM)

```mermaid
stateDiagram-v2
    [*] --> borrador : crear

    borrador --> rechazada_auto : campos faltantes
    borrador --> enviada : doc completo

    enviada --> en_revision : revisor toma

    en_revision --> rechazada : revisor rechaza
    en_revision --> aprobada : doble visto bueno

    aprobada --> oficial : marcar oficial

    oficial --> reemplazada : nueva versión oficial

    rechazada --> [*]
    rechazada_auto --> [*]
    reemplazada --> [*]
```

---

## Reglas de Negocio Clave

| Regla | Detalle |
|-------|---------|
| **RN-01** | Una `InstanciaPresentacion` cambia de estado automáticamente según fechas |
| **RN-03** | Para pasar a `oficial` se requiere doble aprobación (moderadora + coordinador) |
| **RN-06** | Un documento Word debe contener los 7 campos obligatorios para enviarse |
| **RN-08** | Una entrega después de `fecha_limite` se marca como tardía con días de atraso |
| **RN-09** | Existe como máximo una `Planificacion` por combinación (materia, profesor, instancia) |

---

## Próximas entidades (Fase 5)

| Entidad | Descripción |
|---------|-------------|
| `Observacion` | Comentario de rechazo o corrección vinculado a una `Version` |
| `VistosBuenos` | Registro de aprobaciones por revisor para control de doble firma |

# Modelo de Datos

> Diagrama ER simplificado para el MVP. Usa Django ORM.

```mermaid
erDiagram
    Usuario ||--o{ Profesor : "es"
    Usuario {
        int id PK
        string email UK
        string password
        string rol "admin|moderadora|coordinador|profesor|alumno|gestion"
        bool is_active
    }

    Institucion {
        int id PK
        string nombre "ICES|UCSE"
    }

    Carrera ||--|{ Materia : tiene
    Carrera {
        int id PK
        string nombre
        int institucion_id FK
        int coordinador_id FK
        bool activa
    }

    Materia ||--o{ Planificacion : tiene
    Materia {
        int id PK
        string nombre
        int carrera_id FK
        int anio_cursado "1-5"
        string regimen "anual|1cuat|2cuat"
        int profesor_id FK
        bool activa
    }

    Profesor ||--o{ Planificacion : crea
    Profesor {
        int id PK
        int usuario_id FK
        string nombre
        string email
        int institucion_id FK
        bool activo
    }

    Plantilla {
        int id PK
        int institucion_id FK
        file archivo "Word template"
        date vigente_desde
        bool activa
    }

    InstanciaPresentacion ||--|{ Planificacion : recibe
    InstanciaPresentacion {
        int id PK
        string nombre
        int anio_academico
        string periodo "anual|1cuat|2cuat"
        date fecha_apertura
        date fecha_limite
        string estado "programada|abierta|cerrada"
    }

    InstanciaPresentacion }|--|{ Carrera : audiencia

    Planificacion ||--|{ Version : tiene
    Planificacion {
        int id PK
        int materia_id FK
        int profesor_id FK
        int instancia_id FK
        int version_oficial_id FK "nullable"
    }

    Version ||--o{ Revision : tiene
    Version {
        int id PK
        int planificacion_id FK
        int numero "1,2,3..."
        file archivo "Word"
        string estado "borrador|enviada|en_revision|rechazada_auto|rechazada|aprobada|oficial|reemplazada"
        bool entrega_tardia
        datetime fecha_envio
        datetime fecha_creacion
    }

    Revision {
        int id PK
        int version_id FK
        int usuario_id FK "moderadora o coordinador"
        string tipo "aprobacion|rechazo|correccion_leve"
        text observaciones
        datetime fecha
    }

    VistoBueno {
        int id PK
        int version_id FK
        int usuario_id FK
        string rol "moderadora|coordinador"
        datetime fecha
    }
```

---

## Notas del Modelo

### Usuario y Roles

```python
class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = 'admin'
        MODERADORA = 'moderadora'
        COORDINADOR = 'coordinador'
        PROFESOR = 'profesor'
        ALUMNO = 'alumno'
        GESTION = 'gestion'
    
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=Rol.choices)
    
    USERNAME_FIELD = 'email'
```

### Estados de Versión (FSM)

```python
class Version(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = 'borrador'
        ENVIADA = 'enviada'
        EN_REVISION = 'en_revision'
        RECHAZADA_AUTO = 'rechazada_auto'  # Falta campo obligatorio
        RECHAZADA = 'rechazada'            # Por moderadora/coordinador
        APROBADA = 'aprobada'              # Doble visto OK
        OFICIAL = 'oficial'                # Marcada como vigente
        REEMPLAZADA = 'reemplazada'        # Sustituida por nueva oficial
```

Usar **django-fsm** para transiciones controladas.

### Doble Visto (RN-03)

```python
class VistoBueno(models.Model):
    """Registra cada aprobación individual."""
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20)  # moderadora o coordinador
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('version', 'rol')  # Un visto por rol por versión
```

La versión pasa a `APROBADA` solo cuando tiene 2 vistos (moderadora + coordinador).

### Auditoría

Usar **django-simple-history** para tracking automático de cambios en modelos críticos.

### Archivos Word

```python
def planificacion_path(instance, filename):
    # media/planificaciones/2026/carrera_1/materia_5/v1_20260430.docx
    return f"planificaciones/{instance.planificacion.instancia.anio_academico}/{...}"

class Version(models.Model):
    archivo = models.FileField(upload_to=planificacion_path)
```

---

## Índices Recomendados

```python
class Meta:
    indexes = [
        models.Index(fields=['instancia', 'estado']),
        models.Index(fields=['profesor', 'materia']),
        models.Index(fields=['materia', 'instancia']),
    ]
```

---

## Histórico de Instancias

Las instancias de años anteriores **nunca se borran**. Usan un campo `anio_academico` y `estado='cerrada'` para distinguirlas de las activas.

```python
# Consultar histórico
InstanciaPresentacion.objects.filter(anio_academico__lt=2026)

# Consultar activas
InstanciaPresentacion.objects.filter(estado__in=['programada', 'abierta'])
```

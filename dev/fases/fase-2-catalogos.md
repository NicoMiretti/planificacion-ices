# Fase 2 — Catálogos

> Duración estimada: 4-5 horas

## Objetivo

CRUD completo de entidades maestras: Institución, Carrera, Materia, Profesor, Plantilla.

---

## Checklist

- [ ] Modelo `Institucion`
- [ ] Modelo `Carrera` (con coordinador)
- [ ] Modelo `Materia` (con régimen y año)
- [ ] Modelo `Profesor` (vinculado a Usuario)
- [ ] Modelo `Plantilla` (archivo Word por institución)
- [ ] Modelo `MaterialApoyo` (reglamento, calendario, etc.)
- [ ] Admin para todos
- [ ] Vista de listado para moderadora
- [ ] Tests

---

## Modelos

```python
# apps/catalogos/models.py
from django.db import models
from django.conf import settings


class Institucion(models.Model):
    """ICES o UCSE"""
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True)  # 'ICES', 'UCSE'

    class Meta:
        verbose_name_plural = 'instituciones'

    def __str__(self):
        return self.nombre


class Carrera(models.Model):
    nombre = models.CharField(max_length=200)
    institucion = models.ForeignKey(
        Institucion, 
        on_delete=models.PROTECT,
        related_name='carreras'
    )
    coordinador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'rol': 'coordinador'},
        related_name='carreras_coordinadas'
    )
    activa = models.BooleanField(default=True)

    class Meta:
        unique_together = ('nombre', 'institucion')
        ordering = ['institucion', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.institucion.codigo})"


class Materia(models.Model):
    class Regimen(models.TextChoices):
        ANUAL = 'anual', 'Anual'
        PRIMER_CUATRIMESTRE = '1cuat', '1° Cuatrimestre'
        SEGUNDO_CUATRIMESTRE = '2cuat', '2° Cuatrimestre'

    nombre = models.CharField(max_length=200)
    carrera = models.ForeignKey(
        Carrera, 
        on_delete=models.PROTECT,
        related_name='materias'
    )
    anio_cursado = models.PositiveSmallIntegerField(
        help_text='Año de la carrera (1-5)'
    )
    regimen = models.CharField(
        max_length=10,
        choices=Regimen.choices,
        default=Regimen.ANUAL
    )
    profesor_titular = models.ForeignKey(
        'Profesor',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='materias'
    )
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['carrera', 'anio_cursado', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.carrera.nombre}, {self.anio_cursado}° año)"

    @property
    def institucion(self):
        return self.carrera.institucion


class Profesor(models.Model):
    """
    Perfil de profesor, vinculado a Usuario.
    Un Usuario con rol=profesor tiene un Profesor asociado.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_profesor'
    )
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name='profesores'
    )
    legajo = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'profesores'

    def __str__(self):
        return self.usuario.nombre_completo or self.usuario.email

    @property
    def email(self):
        return self.usuario.email

    @property
    def nombre(self):
        return self.usuario.nombre_completo


def plantilla_path(instance, filename):
    return f"plantillas/{instance.institucion.codigo}/{filename}"


class Plantilla(models.Model):
    """Plantilla Word por institución"""
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name='plantillas'
    )
    archivo = models.FileField(upload_to=plantilla_path)
    descripcion = models.CharField(max_length=200, blank=True)
    vigente_desde = models.DateField()
    activa = models.BooleanField(default=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-vigente_desde']

    def __str__(self):
        return f"Plantilla {self.institucion.codigo} ({self.vigente_desde})"

    @classmethod
    def vigente(cls, institucion):
        """Retorna la plantilla activa más reciente para una institución"""
        return cls.objects.filter(
            institucion=institucion,
            activa=True
        ).first()


def material_path(instance, filename):
    return f"materiales/{instance.tipo}/{filename}"


class MaterialApoyo(models.Model):
    """Reglamento, calendario, guía APA, etc."""
    class Tipo(models.TextChoices):
        REGLAMENTO = 'reglamento', 'Reglamento'
        CALENDARIO = 'calendario', 'Calendario Académico'
        GUIA_APA = 'guia_apa', 'Guía APA'
        DOC_ORIENTADOR = 'doc_orientador', 'Documento Orientador'
        OTRO = 'otro', 'Otro'

    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    nombre = models.CharField(max_length=200)
    archivo = models.FileField(upload_to=material_path)
    descripcion = models.TextField(blank=True)
    anio_academico = models.PositiveSmallIntegerField(
        help_text='Año académico al que aplica'
    )
    activo = models.BooleanField(default=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'materiales de apoyo'
        ordering = ['-anio_academico', 'tipo']

    def __str__(self):
        return f"{self.nombre} ({self.anio_academico})"
```

---

## Signals para crear Profesor automáticamente

```python
# apps/catalogos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.usuarios.models import Usuario
from .models import Profesor, Institucion


@receiver(post_save, sender=Usuario)
def crear_perfil_profesor(sender, instance, created, **kwargs):
    """
    Cuando se crea un usuario con rol profesor,
    crear automáticamente su perfil Profesor.
    """
    if created and instance.rol == Usuario.Rol.PROFESOR:
        # Por defecto asignar a ICES, se puede cambiar después
        institucion_default = Institucion.objects.first()
        if institucion_default:
            Profesor.objects.get_or_create(
                usuario=instance,
                defaults={'institucion': institucion_default}
            )
```

```python
# apps/catalogos/apps.py
from django.apps import AppConfig


class CatalogosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.catalogos'

    def ready(self):
        import apps.catalogos.signals  # noqa
```

---

## Admin

```python
# apps/catalogos/admin.py
from django.contrib import admin
from .models import Institucion, Carrera, Materia, Profesor, Plantilla, MaterialApoyo


@admin.register(Institucion)
class InstitucionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'institucion', 'coordinador', 'activa')
    list_filter = ('institucion', 'activa')
    search_fields = ('nombre',)


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'carrera', 'anio_cursado', 'regimen', 'profesor_titular', 'activa')
    list_filter = ('carrera__institucion', 'carrera', 'anio_cursado', 'regimen', 'activa')
    search_fields = ('nombre', 'profesor_titular__usuario__nombre_completo')
    autocomplete_fields = ('profesor_titular',)


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'institucion', 'activo')
    list_filter = ('institucion', 'activo')
    search_fields = ('usuario__email', 'usuario__nombre_completo')


@admin.register(Plantilla)
class PlantillaAdmin(admin.ModelAdmin):
    list_display = ('institucion', 'vigente_desde', 'activa', 'fecha_carga')
    list_filter = ('institucion', 'activa')


@admin.register(MaterialApoyo)
class MaterialApoyoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'anio_academico', 'activo')
    list_filter = ('tipo', 'anio_academico', 'activo')
```

---

## Fixture de datos iniciales

```python
# apps/catalogos/management/commands/cargar_datos_iniciales.py
from django.core.management.base import BaseCommand
from apps.catalogos.models import Institucion


class Command(BaseCommand):
    help = 'Carga datos iniciales de instituciones'

    def handle(self, *args, **options):
        instituciones = [
            {'nombre': 'Instituto de Ciencias y Estudios Superiores', 'codigo': 'ICES'},
            {'nombre': 'Universidad Católica de Santiago del Estero', 'codigo': 'UCSE'},
        ]
        
        for inst in instituciones:
            obj, created = Institucion.objects.get_or_create(
                codigo=inst['codigo'],
                defaults={'nombre': inst['nombre']}
            )
            status = 'Creada' if created else 'Ya existía'
            self.stdout.write(f"{status}: {obj}")

        self.stdout.write(self.style.SUCCESS('Datos iniciales cargados'))
```

```bash
python manage.py cargar_datos_iniciales
```

---

## Tests

```python
# apps/catalogos/tests/test_models.py
import pytest
from apps.catalogos.models import Institucion, Carrera, Materia, Profesor
from apps.usuarios.models import Usuario


@pytest.mark.django_db
class TestCatalogos:
    @pytest.fixture
    def institucion(self):
        return Institucion.objects.create(nombre='ICES', codigo='ICES')

    @pytest.fixture
    def carrera(self, institucion):
        return Carrera.objects.create(
            nombre='Ingeniería en Sistemas',
            institucion=institucion
        )

    def test_crear_materia(self, carrera):
        materia = Materia.objects.create(
            nombre='Programación I',
            carrera=carrera,
            anio_cursado=1,
            regimen=Materia.Regimen.ANUAL
        )
        assert materia.institucion == carrera.institucion

    def test_profesor_signal(self, institucion):
        """Al crear usuario profesor, se crea perfil Profesor"""
        usuario = Usuario.objects.create_user(
            email='profe@ices.edu',
            password='test1234',
            rol=Usuario.Rol.PROFESOR
        )
        assert hasattr(usuario, 'perfil_profesor')
        assert usuario.perfil_profesor.institucion is not None
```

---

## Verificación

```bash
# Migraciones
python manage.py makemigrations catalogos
python manage.py migrate

# Cargar instituciones
python manage.py cargar_datos_iniciales

# Tests
pytest apps/catalogos/tests/ -v

# Verificar en admin que puedes:
# - Crear carreras asociadas a ICES/UCSE
# - Crear materias con régimen anual/cuatrimestral
# - Subir plantillas Word
```

✅ **Fase 2 completa cuando**: Puedes crear la estructura Institución → Carrera → Materia → Profesor desde el admin.

---

## Siguiente: [Fase 3 - Instancias](fase-3-instancias.md)

"""
Modelos de catálogos: Institución, Carrera, Materia, Profesor, Plantilla, MaterialApoyo.
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel, ActivableModel


class Institucion(models.Model):
    """
    Institución educativa: ICES o UCSE.
    Determina qué plantilla usa cada profesor.
    """
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(
        max_length=10, 
        unique=True,
        help_text='Código corto (ICES, UCSE)'
    )

    class Meta:
        verbose_name = 'institución'
        verbose_name_plural = 'instituciones'
        ordering = ['nombre']

    def __str__(self):
        return self.codigo


class Carrera(TimeStampedModel, ActivableModel):
    """
    Carrera académica. Pertenece a una institución y tiene un coordinador.
    """
    nombre = models.CharField(max_length=200)
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name='carreras'
    )
    coordinador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'coordinador'},
        related_name='carreras_coordinadas',
        help_text='Coordinador de la carrera (para doble aprobación)'
    )

    class Meta:
        verbose_name = 'carrera'
        verbose_name_plural = 'carreras'
        unique_together = ('nombre', 'institucion')
        ordering = ['institucion', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.institucion.codigo})"


class Profesor(TimeStampedModel, ActivableModel):
    """
    Perfil de profesor vinculado a un Usuario.
    Un usuario con rol=profesor tiene un Profesor asociado.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_profesor'
    )
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name='profesores',
        help_text='Institución para notificaciones y plantilla'
    )

    class Meta:
        verbose_name = 'profesor'
        verbose_name_plural = 'profesores'
        ordering = ['usuario__nombre_completo', 'usuario__email']

    def __str__(self):
        return self.usuario.nombre_completo or self.usuario.email

    @property
    def email(self):
        return self.usuario.email

    @property
    def nombre(self):
        return self.usuario.nombre_completo or self.usuario.email


class Materia(TimeStampedModel, ActivableModel):
    """
    Materia de una carrera con su régimen y profesor titular.
    """
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
        verbose_name='año de cursado',
        help_text='Año de la carrera (1-5)'
    )
    regimen = models.CharField(
        max_length=10,
        choices=Regimen.choices,
        default=Regimen.ANUAL,
        verbose_name='régimen'
    )
    profesor_titular = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materias',
        help_text='Profesor titular de la materia'
    )

    class Meta:
        verbose_name = 'materia'
        verbose_name_plural = 'materias'
        ordering = ['carrera', 'anio_cursado', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.carrera.nombre}, {self.anio_cursado}° año)"

    @property
    def institucion(self):
        """Institución de la materia (heredada de la carrera)."""
        return self.carrera.institucion


def plantilla_path(instance, filename):
    """Path para archivos de plantilla."""
    return f"plantillas/{instance.institucion.codigo}/{filename}"


class Plantilla(TimeStampedModel, ActivableModel):
    """
    Plantilla Word para planificaciones, una por institución.
    """
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name='plantillas'
    )
    archivo = models.FileField(
        upload_to=plantilla_path,
        help_text='Archivo Word (.doc, .docx)'
    )
    descripcion = models.CharField(max_length=200, blank=True)
    vigente_desde = models.DateField(
        verbose_name='vigente desde',
        help_text='Fecha desde la cual esta plantilla es la oficial'
    )

    class Meta:
        verbose_name = 'plantilla'
        verbose_name_plural = 'plantillas'
        ordering = ['-vigente_desde']

    def __str__(self):
        return f"Plantilla {self.institucion.codigo} ({self.vigente_desde})"

    @classmethod
    def vigente_para(cls, institucion):
        """
        Retorna la plantilla activa más reciente para una institución.
        """
        return cls.objects.filter(
            institucion=institucion,
            activo=True
        ).order_by('-vigente_desde').first()


def material_path(instance, filename):
    """Path para archivos de material de apoyo."""
    return f"materiales/{instance.tipo}/{filename}"


class MaterialApoyo(TimeStampedModel, ActivableModel):
    """
    Materiales de apoyo: reglamento, calendario, guía APA, etc.
    """
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
        verbose_name='año académico',
        help_text='Año académico al que aplica (ej: 2026)'
    )

    class Meta:
        verbose_name = 'material de apoyo'
        verbose_name_plural = 'materiales de apoyo'
        ordering = ['-anio_academico', 'tipo']

    def __str__(self):
        return f"{self.nombre} ({self.anio_academico})"

"""
Modelos de catálogos: Institución, Carrera, Materia, Profesor, Plantilla, MaterialApoyo,
TipoPlanificacion.
"""
from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from apps.core.models import TimeStampedModel, ActivableModel


class TipoPlanificacion(TimeStampedModel):
    """
    Tipo de planificación académica (ej: Planificación ICES, Planificación UCSE).
    Define el título, descripción, lista libre de secciones obligatorias que el
    documento Word debe contener, y un link a documentación adicional.
    """
    titulo = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True)
    campos_obligatorios = models.JSONField(
        default=list,
        help_text='Lista de secciones/campos que el documento Word debe contener (texto libre).',
    )
    link_documentacion = models.URLField(
        blank=True,
        verbose_name='link a documentación',
        help_text='URL a guía o documentación adicional para este tipo.',
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'tipo de planificación'
        verbose_name_plural = 'tipos de planificación'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    @property
    def en_uso(self):
        """True si al menos una InstanciaPresentacion usa este tipo."""
        return self.instancias.exists()


class Institucion(TimeStampedModel):
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
    history = HistoricalRecords()

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
    history = HistoricalRecords()

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

    history = HistoricalRecords()

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

    history = HistoricalRecords()

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
    """
    Ruta estandarizada para plantillas Word:
      plantillas/{institucion}/vigente_{fecha}.ext

    Ejemplo:
      plantillas/ices/vigente_2026-03-01.docx
    """
    import os
    ext = os.path.splitext(filename)[1].lower() or '.docx'
    cod = instance.institucion.codigo.lower()
    return f"plantillas/{cod}/vigente_{instance.vigente_desde}{ext}"


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
    history = HistoricalRecords()

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
    """
    Ruta estandarizada para materiales de apoyo:
      materiales/{tipo}/{anio}/{id}.ext

    Ejemplo:
      materiales/reglamento/2026/5.pdf
    """
    import os
    ext = os.path.splitext(filename)[1].lower()
    pk  = instance.pk or 'nuevo'
    return f"materiales/{instance.tipo}/{instance.anio_academico}/{pk}{ext}"


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
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'material de apoyo'
        verbose_name_plural = 'materiales de apoyo'
        ordering = ['-anio_academico', 'tipo']

    def __str__(self):
        return f"{self.nombre} ({self.anio_academico})"

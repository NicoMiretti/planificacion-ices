"""
Modelos para el circuito de revisión:
- Revision: registra cada acción (tomar, aprobar, rechazar, corregir)
- VistoBueno: control de doble aprobación (moderadora + coordinador)
"""
import os
from django.conf import settings
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


def correccion_path(instance, filename):
    """
    Ruta estandarizada para archivos de correcciones:
      correcciones/{anio}/{institucion}/carrera_{id}/materia_{id}/prof_{id}_v{n}_corr.ext

    Ejemplo:
      correcciones/2026/ices/carrera_3/materia_12/prof_7_v2_corr.docx
    """
    ext = os.path.splitext(filename)[1].lower() or '.docx'
    version = instance.version
    if version:
        p    = version.planificacion
        anio = p.instancia.anio_academico
        cod  = p.materia.carrera.institucion.codigo.lower()
        return (
            f"correcciones/{anio}/{cod}/"
            f"carrera_{p.materia.carrera_id}/"
            f"materia_{p.materia_id}/"
            f"prof_{p.profesor_id}_v{version.numero}_corr{ext}"
        )
    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    return f"correcciones/sin_clasificar/{ts}{ext}"


class Revision(models.Model):
    """Registra cada acción de revisión sobre una planificación (a lo largo de todas sus versiones)."""

    class Tipo(models.TextChoices):
        TOMAR = 'tomar', 'Revisión iniciada'
        APROBAR = 'aprobar', 'Aprobar'
        RECHAZAR = 'rechazar', 'Rechazar'
        CORRECCION_LEVE = 'correccion_leve', 'Corrección leve'

    planificacion = models.ForeignKey(
        'planificaciones.Planificacion',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='revisiones'
    )
    version = models.ForeignKey(
        'planificaciones.Version',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisiones',
        help_text='Versión específica a la que corresponde esta acción'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones de rechazo o comentarios de aprobación'
    )
    detalle_correccion = models.TextField(
        blank=True,
        help_text='Descripción de la corrección aplicada (para corrección leve)'
    )
    archivo_corregido = models.FileField(
        upload_to=correccion_path,
        null=True,
        blank=True,
        help_text='Documento con la corrección leve (opcional)'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'revisión'
        verbose_name_plural = 'revisiones'

    def __str__(self):
        return f"{self.get_tipo_display()} por {self.usuario} — {self.version}"


class VistoBueno(models.Model):
    """
    Registra la aprobación de un revisor específico.
    Se necesitan 2 (moderadora + coordinador de la carrera) para marcar la versión como oficial.
    """
    version = models.ForeignKey(
        'planificaciones.Version',
        on_delete=models.CASCADE,
        related_name='vistos_buenos'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    rol = models.CharField(
        max_length=20,
        help_text="'moderadora' o 'coordinador'"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('version', 'rol')
        verbose_name = 'visto bueno'
        verbose_name_plural = 'vistos buenos'

    def __str__(self):
        return f"VºBº {self.rol} — {self.version}"

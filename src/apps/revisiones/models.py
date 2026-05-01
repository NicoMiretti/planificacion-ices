"""
Modelos para el circuito de revisión:
- Revision: registra cada acción (tomar, aprobar, rechazar, corregir)
- VistoBueno: control de doble aprobación (moderadora + coordinador)
"""
from django.conf import settings
from django.db import models


class Revision(models.Model):
    """Registra cada acción de revisión sobre una versión."""

    class Tipo(models.TextChoices):
        TOMAR = 'tomar', 'Revisión iniciada'
        APROBAR = 'aprobar', 'Aprobar'
        RECHAZAR = 'rechazar', 'Rechazar'
        CORRECCION_LEVE = 'correccion_leve', 'Corrección leve'

    version = models.ForeignKey(
        'planificaciones.Version',
        on_delete=models.CASCADE,
        related_name='revisiones'
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
        upload_to='correcciones/',
        null=True,
        blank=True,
        help_text='Documento con la corrección leve (opcional)'
    )
    fecha = models.DateTimeField(auto_now_add=True)

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

    class Meta:
        unique_together = ('version', 'rol')
        verbose_name = 'visto bueno'
        verbose_name_plural = 'vistos buenos'

    def __str__(self):
        return f"VºBº {self.rol} — {self.version}"

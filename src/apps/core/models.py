"""
Modelos base y mixins reutilizables.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    Mixin abstracto que agrega campos de timestamp.
    """
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActivableModel(models.Model):
    """
    Mixin abstracto para modelos con estado activo/inactivo.
    """
    activo = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def activar(self):
        self.activo = True
        self.save(update_fields=['activo'])

    def desactivar(self):
        self.activo = False
        self.save(update_fields=['activo'])

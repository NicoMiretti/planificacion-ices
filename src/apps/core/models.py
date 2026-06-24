"""
Modelos base y mixins reutilizables.
"""
from django.conf import settings
from django.db import models


def _get_current_user():
    """Retorna el usuario autenticado de la request actual (vía middleware de simple_history)."""
    try:
        from simple_history.middleware import HistoryRequestMiddleware
        request = HistoryRequestMiddleware.get_current_request()
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return request.user
    except Exception:
        pass
    return None


class TimeStampedModel(models.Model):
    """
    Mixin abstracto que agrega campos de auditoría: fechas y usuario que modificó.
    """
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name='+',
        verbose_name='modificado por',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = _get_current_user()
        if user:
            self.modificado_por = user
            # Si se usa update_fields, agregar modificado_por para que también se persista
            update_fields = kwargs.get('update_fields')
            if update_fields is not None and 'modificado_por' not in update_fields:
                kwargs['update_fields'] = list(update_fields) + ['modificado_por']
        super().save(*args, **kwargs)


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

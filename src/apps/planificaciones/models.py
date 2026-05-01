"""
Modelos para el circuito de planificaciones:
- Planificacion: agrupa todas las versiones de una materia/instancia
- Version: una versión específica con FSM de estados
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition


def version_path(instance, filename):
    """Ruta: media/planificaciones/<anio>/carrera_<id>/materia_<id>/prof_<id>_v<n>_<ts>.docx"""
    p = instance.planificacion
    anio = p.instancia.anio_academico
    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    return (
        f"planificaciones/{anio}/"
        f"carrera_{p.materia.carrera_id}/"
        f"materia_{p.materia_id}/"
        f"prof_{p.profesor_id}_v{instance.numero}_{ts}.docx"
    )


class Planificacion(models.Model):
    """
    Agrupa todas las versiones de una planificación para una materia en una instancia.
    Hay una planificacion por (materia, profesor, instancia).
    """
    materia = models.ForeignKey(
        'catalogos.Materia',
        on_delete=models.PROTECT,
        related_name='planificaciones'
    )
    profesor = models.ForeignKey(
        'catalogos.Profesor',
        on_delete=models.PROTECT,
        related_name='planificaciones'
    )
    instancia = models.ForeignKey(
        'instancias.InstanciaPresentacion',
        on_delete=models.PROTECT,
        related_name='planificaciones'
    )

    # Referencia a la versión oficial vigente
    version_oficial = models.OneToOneField(
        'Version',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='es_oficial_de'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('materia', 'profesor', 'instancia')
        verbose_name = 'planificación'
        verbose_name_plural = 'planificaciones'

    def __str__(self):
        return f"{self.materia.nombre} - {self.profesor} ({self.instancia})"

    @property
    def ultima_version(self):
        """Versión con número más alto."""
        return self.versiones.order_by('-numero').first()

    @property
    def tiene_oficial(self):
        return self.version_oficial is not None

    def siguiente_numero_version(self):
        """Calcula el número de la próxima versión."""
        ultima = self.versiones.aggregate(models.Max('numero'))['numero__max']
        return (ultima or 0) + 1


class Version(models.Model):
    """
    Una versión específica de una planificación.
    Usa django-fsm para controlar transiciones de estado.
    """
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        ENVIADA = 'enviada', 'Enviada'
        EN_REVISION = 'en_revision', 'En Revisión'
        RECHAZADA_AUTO = 'rechazada_auto', 'Rechazada (Automático)'
        RECHAZADA = 'rechazada', 'Rechazada'
        APROBADA = 'aprobada', 'Aprobada'
        OFICIAL = 'oficial', 'Oficial Vigente'
        REEMPLAZADA = 'reemplazada', 'Reemplazada'

    planificacion = models.ForeignKey(
        Planificacion,
        on_delete=models.CASCADE,
        related_name='versiones'
    )
    numero = models.PositiveSmallIntegerField()
    archivo = models.FileField(upload_to=version_path)

    estado = FSMField(
        default=Estado.BORRADOR,
        choices=Estado.choices
    )

    # Marca de entrega tardía
    entrega_tardia = models.BooleanField(default=False)
    dias_atraso = models.PositiveSmallIntegerField(default=0)

    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    # Campos faltantes detectados por validación automática
    campos_faltantes = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de campos obligatorios faltantes'
    )

    class Meta:
        ordering = ['-numero']
        unique_together = ('planificacion', 'numero')
        verbose_name = 'versión'
        verbose_name_plural = 'versiones'

    def __str__(self):
        return f"v{self.numero} - {self.planificacion.materia.nombre} ({self.get_estado_display()})"

    # === Transiciones FSM ===

    @transition(field=estado, source=Estado.BORRADOR, target=Estado.RECHAZADA_AUTO)
    def rechazar_automaticamente(self, campos_faltantes):
        """Rechazo automático por falta de campos obligatorios."""
        self.campos_faltantes = campos_faltantes

    @transition(field=estado, source=Estado.BORRADOR, target=Estado.ENVIADA)
    def enviar(self):
        """Envío exitoso tras validación."""
        self.fecha_envio = timezone.now()
        self._calcular_tardia()

    @transition(field=estado, source=Estado.ENVIADA, target=Estado.EN_REVISION)
    def tomar_revision(self):
        """Un revisor toma la planificación para revisar."""
        pass

    @transition(field=estado, source=Estado.EN_REVISION, target=Estado.RECHAZADA)
    def rechazar(self):
        """Rechazo por revisor con observaciones."""
        pass

    @transition(field=estado, source=Estado.EN_REVISION, target=Estado.APROBADA)
    def aprobar(self):
        """Aprobación completada."""
        self.fecha_aprobacion = timezone.now()

    @transition(field=estado, source=Estado.APROBADA, target=Estado.OFICIAL)
    def marcar_oficial(self):
        """Marcar como versión oficial vigente."""
        planif = self.planificacion
        # Reemplazar la oficial anterior si existe
        if planif.version_oficial and planif.version_oficial != self:
            planif.version_oficial.reemplazar()
            planif.version_oficial.save()
        planif.version_oficial = self
        planif.save()

    @transition(field=estado, source=Estado.OFICIAL, target=Estado.REEMPLAZADA)
    def reemplazar(self):
        """Esta versión fue reemplazada por una nueva oficial."""
        pass

    def _calcular_tardia(self):
        """Calcula si la entrega es tardía respecto a fecha_limite."""
        fecha_limite = self.planificacion.instancia.fecha_limite
        hoy = timezone.now().date()
        if hoy > fecha_limite:
            self.entrega_tardia = True
            self.dias_atraso = (hoy - fecha_limite).days
        else:
            self.entrega_tardia = False
            self.dias_atraso = 0

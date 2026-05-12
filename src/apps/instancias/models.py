"""
Modelo InstanciaPresentacion.
Permite a la moderadora crear convocatorias para presentación de planificaciones.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.catalogos.models import Carrera, Materia, Institucion


class InstanciaQuerySet(models.QuerySet):
    """QuerySet con métodos de consulta comunes - soporta chaining."""

    def activas(self):
        """Instancias que aceptan envíos (programadas o abiertas)."""
        return self.filter(estado__in=['programada', 'abierta'])

    def abiertas(self):
        """Instancias actualmente abiertas."""
        return self.filter(estado='abierta')

    def del_anio(self, anio):
        """Instancias de un año académico específico."""
        return self.filter(anio_academico=anio)

    def historicas(self):
        """Instancias cerradas o de años anteriores."""
        anio_actual = timezone.now().year
        return self.filter(
            models.Q(anio_academico__lt=anio_actual) |
            models.Q(estado='cerrada')
        )

    def para_profesor(self, usuario):
        """
        Instancias donde el usuario (profesor) tiene materias asignadas.
        Requiere que el usuario tenga un perfil_profesor.
        """
        if not hasattr(usuario, 'perfil_profesor'):
            return self.none()

        profesor = usuario.perfil_profesor
        carreras_profesor = Materia.objects.filter(
            profesor_titular=profesor,
            activo=True
        ).values_list('carrera_id', flat=True)

        return self.filter(carreras__id__in=carreras_profesor).distinct()


class InstanciaManager(models.Manager):
    """Manager que expone el QuerySet personalizado."""

    def get_queryset(self):
        return InstanciaQuerySet(self.model, using=self._db)

    def activas(self):
        return self.get_queryset().activas()

    def abiertas(self):
        return self.get_queryset().abiertas()

    def del_anio(self, anio):
        return self.get_queryset().del_anio(anio)

    def historicas(self):
        return self.get_queryset().historicas()

    def para_profesor(self, usuario):
        return self.get_queryset().para_profesor(usuario)


class InstanciaPresentacion(models.Model):
    """
    Una instancia de presentación es una convocatoria para que los profesores
    presenten sus planificaciones. Tiene fechas de apertura/cierre y define
    una audiencia (qué carreras/materias deben presentar).
    """
    
    class Periodo(models.TextChoices):
        ANUAL = 'anual', 'Anual'
        PRIMER_CUATRIMESTRE = '1cuat', '1° Cuatrimestre'
        SEGUNDO_CUATRIMESTRE = '2cuat', '2° Cuatrimestre'

    class Estado(models.TextChoices):
        PROGRAMADA = 'programada', 'Programada'
        ABIERTA = 'abierta', 'Abierta'
        CERRADA = 'cerrada', 'Cerrada'

    nombre = models.CharField(
        max_length=200,
        help_text='Ej: "Planificaciones Anuales 2026"'
    )
    anio_academico = models.PositiveSmallIntegerField(
        help_text='Año académico (ej: 2026)'
    )
    periodo = models.CharField(
        max_length=10,
        choices=Periodo.choices
    )
    
    # Audiencia: a qué carreras aplica
    carreras = models.ManyToManyField(
        Carrera,
        related_name='instancias',
        help_text='Carreras incluidas en esta instancia'
    )
    
    # Filtros adicionales de audiencia
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text='Filtrar por institución (vacío = todas)'
    )
    solo_regimen = models.CharField(
        max_length=10,
        choices=Materia.Regimen.choices,
        blank=True,
        help_text='Filtrar materias por régimen (vacío = todos)'
    )
    
    # Fechas
    fecha_apertura = models.DateField(
        help_text='Fecha desde la cual se aceptan envíos'
    )
    fecha_limite = models.DateField(
        help_text='Fecha límite para envíos (después son tardíos)'
    )
    
    # Estado (se actualiza automáticamente según fechas)
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PROGRAMADA
    )
    
    # Metadata
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='instancias_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    objects = InstanciaManager()

    class Meta:
        ordering = ['-anio_academico', '-fecha_apertura']
        verbose_name = 'instancia de presentación'
        verbose_name_plural = 'instancias de presentación'

    def __str__(self):
        return f"{self.nombre} ({self.anio_academico})"

    def save(self, *args, **kwargs):
        # Auto-actualizar estado según fechas
        self._actualizar_estado()
        super().save(*args, **kwargs)

    def _actualizar_estado(self):
        """Actualiza el estado según las fechas actuales."""
        hoy = timezone.now().date()
        # No reabrir instancias cerradas manualmente
        if self.estado != self.Estado.CERRADA:
            if hoy < self.fecha_apertura:
                self.estado = self.Estado.PROGRAMADA
            elif hoy <= self.fecha_limite:
                self.estado = self.Estado.ABIERTA
            else:
                # Pasó la fecha límite - sigue aceptando tardías
                self.estado = self.Estado.ABIERTA

    @property
    def esta_abierta(self):
        """Indica si la instancia está actualmente abierta."""
        return self.estado == self.Estado.ABIERTA

    @property
    def acepta_envios(self):
        """Indica si acepta envíos (abierta o programada)."""
        return self.estado in [self.Estado.ABIERTA]

    @property
    def es_tardia(self):
        """Indica si estamos después de la fecha límite."""
        return timezone.now().date() > self.fecha_limite

    def materias_audiencia(self):
        """
        Retorna las materias que deben presentar en esta instancia.
        Filtra por carreras + régimen + institución si aplica.
        Cuando solo_regimen está vacío, usa el período de la instancia como régimen por defecto.
        """
        materias = Materia.objects.filter(
            carrera__in=self.carreras.all(),
            activo=True
        )

        # Filtrar por régimen: usa solo_regimen si está seteado, sino el periodo de la instancia
        regimen_efectivo = self.solo_regimen or self.periodo
        materias = materias.filter(regimen=regimen_efectivo)

        # Filtrar por institución si está especificado
        if self.institucion:
            materias = materias.filter(carrera__institucion=self.institucion)
        
        return materias.select_related('carrera', 'profesor_titular')

    def profesores_audiencia(self):
        """Profesores que deben presentar en esta instancia."""
        from apps.catalogos.models import Profesor
        materias = self.materias_audiencia()
        profesor_ids = materias.values_list(
            'profesor_titular_id', flat=True
        ).distinct()
        return Profesor.objects.filter(id__in=profesor_ids, activo=True)

    def cantidad_materias(self):
        """Cantidad de materias en la audiencia."""
        return self.materias_audiencia().count()

    def cantidad_profesores(self):
        """Cantidad de profesores en la audiencia."""
        return self.profesores_audiencia().count()

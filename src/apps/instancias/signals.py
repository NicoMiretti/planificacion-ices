from django.db.models.signals import m2m_changed
from django.dispatch import receiver


@receiver(m2m_changed, sender='instancias.InstanciaPresentacion_carreras')
def crear_planificaciones_al_agregar_carreras(sender, instance, action, pk_set, **kwargs):
    """
    Cuando se agregan carreras a una instancia, auto-crea una Planificacion
    vacía para cada materia de esas carreras que tenga profesor titular asignado.

    La planificacion queda en estado inicial: el profesor puede cargar su
    primera versión desde la interfaz. Nunca aparece 'Sin planificación'.
    """
    if action != 'post_add' or not pk_set:
        return

    from apps.catalogos.models import Materia
    from apps.planificaciones.models import Planificacion

    # Solo las materias de las carreras recién agregadas
    materias = Materia.objects.filter(
        carrera_id__in=pk_set,
        activo=True,
    ).select_related('profesor_titular')

    # Filtrar por el régimen efectivo de la instancia
    regimen_efectivo = instance.solo_regimen or instance.periodo
    materias = materias.filter(regimen=regimen_efectivo)

    for materia in materias:
        if materia.profesor_titular:
            Planificacion.objects.get_or_create(
                materia=materia,
                profesor=materia.profesor_titular,
                instancia=instance,
            )

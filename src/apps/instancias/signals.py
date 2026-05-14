from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.instancias.models import InstanciaPresentacion


@receiver(m2m_changed, sender=InstanciaPresentacion.carreras.through)
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

    # Filtrar por el régimen según el período de la instancia
    if instance.periodo != 'todos':
        materias = materias.filter(regimen=instance.periodo)

    # Filtrar por años de cursado por carrera si se especificaron
    # anios_cursado es un dict {str(carrera_id): [años]}
    if instance.anios_cursado and isinstance(instance.anios_cursado, dict):
        from django.db.models import Q
        filtro_anios = Q()
        for carrera_id_str, anios in instance.anios_cursado.items():
            cid = int(carrera_id_str)
            if cid in pk_set and anios:
                filtro_anios |= Q(carrera_id=cid, anio_cursado__in=anios)
        if filtro_anios:
            materias = materias.filter(filtro_anios)

    for materia in materias:
        if materia.profesor_titular:
            Planificacion.objects.get_or_create(
                materia=materia,
                profesor=materia.profesor_titular,
                instancia=instance,
            )

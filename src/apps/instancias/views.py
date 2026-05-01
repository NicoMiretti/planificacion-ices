"""
Vistas para el módulo de instancias de presentación.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from apps.usuarios.decorators import solo_moderadora, revisores
from .models import InstanciaPresentacion


@login_required
@revisores
def lista_instancias(request):
    """Vista para moderadora: todas las instancias."""
    instancias = InstanciaPresentacion.objects.all()
    
    # Filtros opcionales
    anio = request.GET.get('anio')
    if anio:
        try:
            instancias = instancias.filter(anio_academico=int(anio))
        except ValueError:
            pass
    
    estado = request.GET.get('estado')
    if estado:
        instancias = instancias.filter(estado=estado)
    
    context = {
        'instancias': instancias,
        'anios_disponibles': InstanciaPresentacion.objects.values_list(
            'anio_academico', flat=True
        ).distinct().order_by('-anio_academico'),
        'estados': InstanciaPresentacion.Estado.choices,
        'filtro_anio': anio,
        'filtro_estado': estado,
    }
    return render(request, 'instancias/lista.html', context)


@login_required
def mis_instancias(request):
    """Vista para profesor: sus instancias asignadas."""
    if not hasattr(request.user, 'perfil_profesor'):
        return render(request, 'instancias/no_profesor.html')

    profesor = request.user.perfil_profesor
    instancias = InstanciaPresentacion.objects.para_profesor(request.user)

    from apps.planificaciones.models import Planificacion, Version

    def resumen_instancia(inst):
        """Devuelve dict de conteos de estados de planificaciones en la instancia."""
        planifs = Planificacion.objects.filter(
            instancia=inst, profesor=profesor
        ).prefetch_related('versiones')
        total_mats = inst.materias_audiencia().filter(profesor_titular=profesor).count()
        estados = {'rechazadas': 0, 'en_revision': 0, 'enviadas': 0,
                   'borradores': 0, 'oficiales': 0, 'sin_cargar': 0}
        planif_ids = set()
        for p in planifs:
            planif_ids.add(p.materia_id)
            ultima = p.versiones.order_by('-numero').first()
            if ultima:
                if ultima.estado in ('rechazada', 'rechazada_auto'):
                    estados['rechazadas'] += 1
                elif ultima.estado == 'en_revision':
                    estados['en_revision'] += 1
                elif ultima.estado == 'enviada':
                    estados['enviadas'] += 1
                elif ultima.estado == 'borrador':
                    estados['borradores'] += 1
                elif ultima.estado in ('oficial', 'aprobada'):
                    estados['oficiales'] += 1
        estados['sin_cargar'] = total_mats - len(planif_ids)
        return estados

    activas_list = []
    for inst in instancias.activas():
        activas_list.append((inst, resumen_instancia(inst)))

    context = {
        'instancias_activas': activas_list,
        'instancias_historicas': instancias.historicas(),
        'profesor': profesor,
        'today': timezone.now().date(),
    }
    return render(request, 'instancias/mis_instancias.html', context)


@login_required
def detalle_instancia(request, pk):
    """Detalle de una instancia con sus materias."""
    instancia = get_object_or_404(InstanciaPresentacion, pk=pk)
    
    materias = instancia.materias_audiencia()
    
    # Si es profesor, filtrar solo sus materias
    if request.user.es_profesor and hasattr(request.user, 'perfil_profesor'):
        materias = materias.filter(profesor_titular=request.user.perfil_profesor)

    # Para profesores: dict materia_id → planificacion existente
    planificaciones_por_materia = {}
    if request.user.es_profesor and hasattr(request.user, 'perfil_profesor'):
        from apps.planificaciones.models import Planificacion
        qs = Planificacion.objects.filter(
            instancia=instancia,
            profesor=request.user.perfil_profesor,
            materia__in=materias
        )
        planificaciones_por_materia = {p.materia_id: p for p in qs}

    # Lista de (materia, planificacion_o_None) para el template
    materias_con_planif = [
        (m, planificaciones_por_materia.get(m.pk))
        for m in materias
    ]

    context = {
        'instancia': instancia,
        'materias': materias,
        'materias_con_planif': materias_con_planif,
        'today': timezone.now().date(),
    }
    return render(request, 'instancias/detalle.html', context)

"""
Vistas para el módulo de instancias de presentación.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from apps.usuarios.decorators import solo_moderadora
from .models import InstanciaPresentacion


@login_required
@solo_moderadora
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
        # No es profesor - mostrar mensaje
        return render(request, 'instancias/no_profesor.html')
    
    profesor = request.user.perfil_profesor
    instancias = InstanciaPresentacion.objects.para_profesor(request.user)
    
    context = {
        'instancias_activas': instancias.activas(),
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

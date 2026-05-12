"""
Vistas para el módulo de instancias de presentación.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from apps.usuarios.decorators import solo_moderadora, revisores
from .models import InstanciaPresentacion
from .forms import InstanciaForm


@login_required
@revisores
def lista_instancias(request):
    """Vista: moderadora ve todas, coordinador solo sus carreras."""
    from apps.catalogos.models import Carrera
    instancias = InstanciaPresentacion.objects.all()

    # Coordinador: solo instancias de sus carreras
    if request.user.es_coordinador:
        mis_carreras = Carrera.objects.filter(
            coordinador=request.user
        ).values_list('id', flat=True)
        instancias = instancias.filter(carreras__in=mis_carreras).distinct()
    
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
        estados = {'rechazadas': 0, 'en_revision': 0,
                   'borradores': 0, 'oficiales': 0, 'sin_cargar': 0}
        for p in planifs:
            ultima = p.versiones.order_by('-numero').first()
            if ultima is None:
                estados['sin_cargar'] += 1
            elif ultima.estado in ('rechazada', 'rechazada_auto'):
                estados['rechazadas'] += 1
            elif ultima.estado == 'en_revision':
                estados['en_revision'] += 1
            elif ultima.estado == 'borrador':
                estados['borradores'] += 1
            elif ultima.estado in ('oficial', 'aprobada'):
                estados['oficiales'] += 1
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
    from apps.catalogos.models import Carrera
    instancia = get_object_or_404(InstanciaPresentacion, pk=pk)

    materias = instancia.materias_audiencia()

    # Filtrar materias según el rol
    if request.user.es_profesor and hasattr(request.user, 'perfil_profesor'):
        materias = materias.filter(profesor_titular=request.user.perfil_profesor)
    elif request.user.es_coordinador:
        mis_carreras = Carrera.objects.filter(coordinador=request.user)
        materias = materias.filter(carrera__in=mis_carreras)
    # Moderadora: ve todas sin filtro

    # Obtener carreras y años disponibles ANTES de aplicar filtros GET
    carreras_disponibles = (
        materias.values_list('carrera__id', 'carrera__nombre')
        .distinct().order_by('carrera__nombre')
    )
    anios_disponibles = (
        materias.values_list('anio_cursado', flat=True)
        .distinct().order_by('anio_cursado')
    )
    carreras_disponibles = list(carreras_disponibles)
    anios_disponibles = list(anios_disponibles)

    # Filtros opcionales por carrera y año (solo si hay más de una opción)
    filtro_carrera = request.GET.get('carrera')
    filtro_anio = request.GET.get('anio')
    if filtro_carrera:
        try:
            materias = materias.filter(carrera_id=int(filtro_carrera))
        except (ValueError, TypeError):
            filtro_carrera = None
    if filtro_anio:
        try:
            materias = materias.filter(anio_cursado=int(filtro_anio))
        except (ValueError, TypeError):
            filtro_anio = None

    planificaciones_por_materia = {}
    from apps.planificaciones.models import Planificacion
    if request.user.es_profesor and hasattr(request.user, 'perfil_profesor'):
        qs = Planificacion.objects.filter(
            instancia=instancia,
            profesor=request.user.perfil_profesor,
            materia__in=materias
        ).prefetch_related('versiones')
        planificaciones_por_materia = {p.materia_id: p for p in qs}
    else:
        # Moderadora, coordinador, admin, revisor: ven la planif del titular
        materias_list = list(materias)
        qs = Planificacion.objects.filter(
            instancia=instancia,
            materia__in=materias_list,
        ).select_related('materia', 'profesor').prefetch_related('versiones')
        # Indexar por materia, priorizando siempre la del profesor titular
        raw = {}
        for p in qs:
            mid = p.materia_id
            titular = p.materia.profesor_titular_id
            if mid not in raw or p.profesor_id == titular:
                raw[mid] = p
        planificaciones_por_materia = raw

    materias_con_planif = [
        (m, planificaciones_por_materia.get(m.pk))
        for m in materias
    ]

    context = {
        'instancia': instancia,
        'materias': materias,
        'materias_con_planif': materias_con_planif,
        'today': timezone.now().date(),
        'carreras_disponibles': carreras_disponibles,
        'anios_disponibles': anios_disponibles,
        'filtro_carrera': filtro_carrera,
        'filtro_anio': filtro_anio,
        'mostrar_filtros': len(carreras_disponibles) > 1 or len(anios_disponibles) > 1,
    }
    return render(request, 'instancias/detalle.html', context)


@login_required
@solo_moderadora
def crear_instancia(request):
    """Vista: moderadora da de alta una nueva instancia de presentación."""
    if request.method == 'POST':
        form = InstanciaForm(request.POST)
        if form.is_valid():
            instancia = form.save(commit=False)
            instancia.creada_por = request.user
            instancia.save()
            form.save_m2m()  # dispara el signal que auto-crea las planificaciones

            messages.success(
                request,
                f'Instancia "{instancia}" creada correctamente.'
            )
            return redirect('instancias:detalle', pk=instancia.pk)
    else:
        form = InstanciaForm()

    return render(request, 'instancias/crear.html', {'form': form})

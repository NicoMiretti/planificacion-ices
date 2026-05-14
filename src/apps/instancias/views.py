"""
Vistas para el módulo de instancias de presentación.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
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
    import json
    if request.method == 'POST':
        form = InstanciaForm(request.POST)
        # Extraer años previos por carrera para re-render en caso de error de validación
        anios_previos = {}
        for key in request.POST:
            if key.startswith('anios_carrera_'):
                cid = key.replace('anios_carrera_', '')
                anios_previos[cid] = request.POST.getlist(key)
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
        anios_previos = {}

    return render(request, 'instancias/crear.html', {
        'form': form,
        'anios_previos_json': json.dumps(anios_previos),
    })


@login_required
@solo_moderadora
def ajax_anios_por_carreras(request):
    """AJAX: devuelve los años de cursado disponibles para las carreras seleccionadas."""
    from apps.catalogos.models import Materia
    carrera_ids = request.GET.getlist('carreras[]')
    if not carrera_ids:
        return JsonResponse({'anios': []})
    try:
        carrera_ids = [int(cid) for cid in carrera_ids]
    except (ValueError, TypeError):
        return JsonResponse({'anios': []})
    anios = list(
        Materia.objects.filter(
            carrera_id__in=carrera_ids,
            activo=True,
        ).values_list('anio_cursado', flat=True).distinct().order_by('anio_cursado')
    )
    return JsonResponse({'anios': anios})


@login_required
@solo_moderadora
def editar_instancia(request, pk):
    """Vista: moderadora edita una instancia existente."""
    import json
    from apps.planificaciones.models import Planificacion, Version

    instancia = get_object_or_404(InstanciaPresentacion, pk=pk)

    total_planif = instancia.planificaciones.count()
    total_versiones = Version.objects.filter(planificacion__instancia=instancia).count()
    planif_con_contenido = instancia.planificaciones.filter(versiones__isnull=False).distinct().count()

    if request.method == 'POST':
        anios_previos = {}
        for key in request.POST:
            if key.startswith('anios_carrera_'):
                cid = key.replace('anios_carrera_', '')
                anios_previos[cid] = request.POST.getlist(key)

        carreras_antes = set(instancia.carreras.values_list('id', flat=True))
        form = InstanciaForm(request.POST, instance=instancia)
        if form.is_valid():
            instancia_guardada = form.save()

            # Limpiar planificaciones vacías de carreras que ya no están
            carreras_despues = set(instancia_guardada.carreras.values_list('id', flat=True))
            carreras_removidas = carreras_antes - carreras_despues
            if carreras_removidas:
                Planificacion.objects.filter(
                    instancia=instancia_guardada,
                    materia__carrera_id__in=carreras_removidas,
                ).filter(versiones__isnull=True).delete()

            # Crear planificaciones para toda la audiencia actual (nueva audiencia completa).
            # Esto cubre: carreras nuevas, años nuevos en carreras existentes, y años
            # que se habían quitado antes y ahora se vuelven a agregar.
            # get_or_create garantiza que no se duplican las existentes.
            creadas = 0
            for materia in instancia_guardada.materias_audiencia():
                if materia.profesor_titular:
                    _, nueva = Planificacion.objects.get_or_create(
                        materia=materia,
                        profesor=materia.profesor_titular,
                        instancia=instancia_guardada,
                    )
                    if nueva:
                        creadas += 1

            messages.success(
                request,
                f'Instancia "{instancia_guardada}" actualizada correctamente.'
                + (f' Se crearon {creadas} planificación/es nuevas.' if creadas else '')
            )
            return redirect('instancias:detalle', pk=instancia_guardada.pk)
    else:
        form = InstanciaForm(instance=instancia)
        anios_previos = {
            str(k): [str(v) for v in vals]
            for k, vals in (instancia.anios_cursado or {}).items()
        }

    return render(request, 'instancias/editar.html', {
        'form': form,
        'instancia': instancia,
        'total_planif': total_planif,
        'total_versiones': total_versiones,
        'planif_con_contenido': planif_con_contenido,
        'anios_previos_json': json.dumps(anios_previos),
    })


@login_required
@solo_moderadora
def eliminar_instancia(request, pk):
    """Vista: moderadora elimina una instancia y todas sus planificaciones."""
    from apps.planificaciones.models import Planificacion, Version

    instancia = get_object_or_404(InstanciaPresentacion, pk=pk)

    total_planif = instancia.planificaciones.count()
    total_versiones = Version.objects.filter(planificacion__instancia=instancia).count()
    planif_con_contenido = instancia.planificaciones.filter(versiones__isnull=False).distinct().count()

    if request.method == 'POST':
        confirmacion = request.POST.get('confirmacion', '').strip()
        if confirmacion != instancia.nombre:
            messages.error(
                request,
                'El nombre ingresado no coincide. La instancia no fue eliminada.'
            )
            return render(request, 'instancias/confirmar_eliminar.html', {
                'instancia': instancia,
                'total_planif': total_planif,
                'total_versiones': total_versiones,
                'planif_con_contenido': planif_con_contenido,
                'error_confirmacion': True,
            })

        nombre = str(instancia)
        instancia.delete()
        messages.success(request, f'La instancia "{nombre}" y todas sus planificaciones fueron eliminadas.')
        return redirect('instancias:lista')

    return render(request, 'instancias/confirmar_eliminar.html', {
        'instancia': instancia,
        'total_planif': total_planif,
        'total_versiones': total_versiones,
        'planif_con_contenido': planif_con_contenido,
        'error_confirmacion': False,
    })


@login_required
@solo_moderadora
def ajax_preview_edicion(request, pk):
    """
    AJAX GET: dado un conjunto propuesto de carreras + años por carrera,
    devuelve cuántas planificaciones se crearían, cuántas se eliminarían
    (sin archivos) y cuántas se conservarían aunque queden fuera (con archivos).
    """
    from apps.catalogos.models import Materia
    from apps.planificaciones.models import Planificacion
    from django.db.models import Q

    instancia = get_object_or_404(InstanciaPresentacion, pk=pk)

    # Leer parámetros de la petición AJAX
    carrera_ids_raw = request.GET.getlist('carreras[]')
    try:
        carrera_ids = [int(c) for c in carrera_ids_raw]
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)

    periodo = request.GET.get('periodo', instancia.periodo)

    # Construir el dict anios_cursado propuesto {carrera_id: [años]}
    anios_propuesto = {}
    for key, val in request.GET.lists():
        if key.startswith('anios_carrera_'):
            try:
                cid = int(key.replace('anios_carrera_', ''))
                anios_propuesto[cid] = [int(v) for v in val]
            except (ValueError, TypeError):
                pass

    # ── Audiencia PROPUESTA ──────────────────────────────────────────────────
    materias_qs = Materia.objects.filter(
        carrera_id__in=carrera_ids,
        activo=True,
        profesor_titular__isnull=False,
    )
    if periodo and periodo != 'todos':
        materias_qs = materias_qs.filter(regimen=periodo)

    if anios_propuesto:
        filtro = Q()
        for cid, anios in anios_propuesto.items():
            if anios:
                filtro |= Q(carrera_id=cid, anio_cursado__in=anios)
        if filtro:
            materias_qs = materias_qs.filter(filtro)

    ids_propuestos = set(materias_qs.values_list('id', flat=True))

    # ── Planificaciones ACTUALES ─────────────────────────────────────────────
    planifs_actuales = list(
        Planificacion.objects.filter(instancia=instancia)
        .select_related('materia')
        .prefetch_related('versiones')
    )
    ids_actuales = {p.materia_id for p in planifs_actuales}

    # Cuántas se van a CREAR (materia en propuesta pero sin planificación existente)
    a_crear = len(ids_propuestos - ids_actuales)

    # Cuántas se van a ELIMINAR (planificación existe, materia queda fuera, sin versiones)
    ids_removidos = ids_actuales - ids_propuestos
    planifs_removidas = [p for p in planifs_actuales if p.materia_id in ids_removidos]
    a_eliminar = sum(1 for p in planifs_removidas if not p.versiones.exists())
    conservadas_con_archivos = sum(1 for p in planifs_removidas if p.versiones.exists())

    return JsonResponse({
        'a_crear': a_crear,
        'a_eliminar': a_eliminar,
        'conservadas_con_archivos': conservadas_con_archivos,
    })

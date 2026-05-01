"""
Vistas para el circuito de revisión.
CU-02 Tablero, CU-03 Aprobar, CU-04 Rechazar, CU-05 Corrección leve.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Exists, OuterRef

from apps.usuarios.decorators import revisores
from apps.planificaciones.models import Planificacion, Version
from apps.catalogos.models import Carrera

from .models import Revision, VistoBueno
from .services import RevisionService
from .forms import RechazarForm, CorreccionLeveForm


@login_required
@revisores
def tablero_revision(request):
    """CU-02: Tablero de planificaciones pendientes de revisión."""
    user = request.user

    versiones = Version.objects.filter(
        estado__in=[Version.Estado.ENVIADA, Version.Estado.EN_REVISION]
    ).select_related(
        'planificacion__materia__carrera__institucion',
        'planificacion__profesor__usuario',
        'planificacion__instancia'
    )

    # Coordinador solo ve sus carreras
    if user.es_coordinador:
        carreras_ids = Carrera.objects.filter(
            coordinador=user
        ).values_list('id', flat=True)
        versiones = versiones.filter(
            planificacion__materia__carrera_id__in=carreras_ids
        )

    # Anotar si el usuario ya dio visto bueno
    versiones = versiones.annotate(
        tiene_mi_visto=Exists(
            VistoBueno.objects.filter(
                version=OuterRef('pk'),
                rol=user.rol
            )
        )
    )

    # Filtros opcionales
    filtros = {}

    carrera_id = request.GET.get('carrera')
    if carrera_id:
        versiones = versiones.filter(planificacion__materia__carrera_id=carrera_id)
        filtros['carrera'] = carrera_id

    estado = request.GET.get('estado')
    if estado:
        versiones = versiones.filter(estado=estado)
        filtros['estado'] = estado

    tardia = request.GET.get('tardia')
    if tardia == '1':
        versiones = versiones.filter(entrega_tardia=True)
        filtros['tardia'] = '1'

    versiones = versiones.order_by('estado', 'fecha_envio')

    context = {
        'versiones': versiones,
        'filtros': filtros,
        'carreras': Carrera.objects.filter(activo=True),
        'estados': [
            (Version.Estado.ENVIADA, 'Enviada'),
            (Version.Estado.EN_REVISION, 'En Revisión'),
        ],
    }
    return render(request, 'revisiones/tablero.html', context)


@login_required
@revisores
def revisar_version(request, version_id):
    """Vista de revisión individual. Toma automáticamente si está enviada."""
    version = get_object_or_404(
        Version.objects.select_related(
            'planificacion__materia__carrera__coordinador',
            'planificacion__profesor__usuario',
            'planificacion__instancia'
        ),
        pk=version_id
    )

    user = request.user

    # Tomar si está enviada
    if version.estado == Version.Estado.ENVIADA:
        try:
            RevisionService.tomar_para_revision(version, user)
            messages.info(request, 'Planificación tomada para revisión.')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('revisiones:tablero')

    # Coordinador solo puede revisar sus carreras
    if user.es_coordinador:
        carrera = version.planificacion.materia.carrera
        if carrera.coordinador != user:
            messages.error(request, 'No tienes acceso a esta planificación.')
            return redirect('revisiones:tablero')

    mi_visto = VistoBueno.objects.filter(version=version, rol=user.rol).first()
    otro_rol = 'coordinador' if user.rol == 'moderadora' else 'moderadora'
    otro_visto = VistoBueno.objects.filter(version=version, rol=otro_rol).first()

    context = {
        'version': version,
        'planificacion': version.planificacion,
        'revisiones': version.revisiones.all(),
        'mi_visto': mi_visto,
        'otro_visto': otro_visto,
        'form_rechazo': RechazarForm(),
        'form_correccion': CorreccionLeveForm() if user.es_moderadora else None,
    }
    return render(request, 'revisiones/revisar.html', context)


@login_required
@revisores
def aprobar_version(request, version_id):
    """CU-03: Aprobar planificación (dar visto bueno)."""
    if request.method != 'POST':
        return redirect('revisiones:revisar', version_id=version_id)

    version = get_object_or_404(Version, pk=version_id)

    try:
        RevisionService.aprobar(version, request.user)
        version.refresh_from_db()

        if version.estado == Version.Estado.OFICIAL:
            messages.success(request, '¡Planificación APROBADA y marcada como OFICIAL! (doble visto completado)')
        else:
            messages.success(request, 'Visto bueno registrado. Falta la aprobación del otro revisor.')

    except ValueError as e:
        messages.error(request, str(e))

    return redirect('revisiones:tablero')


@login_required
@revisores
def rechazar_version(request, version_id):
    """CU-04: Rechazar planificación con observaciones."""
    if request.method != 'POST':
        return redirect('revisiones:revisar', version_id=version_id)

    version = get_object_or_404(Version, pk=version_id)
    form = RechazarForm(request.POST)

    if form.is_valid():
        try:
            RevisionService.rechazar(
                version,
                request.user,
                form.cleaned_data['observaciones']
            )
            messages.success(request, 'Planificación rechazada. El profesor deberá corregir y reenviar.')
        except ValueError as e:
            messages.error(request, str(e))
    else:
        messages.error(request, 'Las observaciones son obligatorias para rechazar.')

    return redirect('revisiones:tablero')


@login_required
@revisores
def correccion_leve(request, version_id):
    """CU-05: Aplicar corrección leve (solo moderadora)."""
    if request.method != 'POST':
        return redirect('revisiones:revisar', version_id=version_id)

    if not request.user.es_moderadora:
        messages.error(request, 'Solo la moderadora puede aplicar correcciones leves.')
        return redirect('revisiones:tablero')

    version = get_object_or_404(Version, pk=version_id)
    form = CorreccionLeveForm(request.POST, request.FILES)

    if form.is_valid():
        try:
            RevisionService.aplicar_correccion_leve(
                version,
                request.user,
                form.cleaned_data['detalle'],
                form.cleaned_data.get('archivo_corregido')
            )
            messages.success(request, 'Corrección leve aplicada y registrada.')
        except ValueError as e:
            messages.error(request, str(e))
    else:
        messages.error(request, 'El detalle de la corrección es obligatorio.')

    return redirect('revisiones:revisar', version_id=version_id)


@login_required
@revisores
def historial_revisiones(request, planificacion_id):
    """Historial completo de revisiones de una planificación."""
    planificacion = get_object_or_404(Planificacion, pk=planificacion_id)

    revisiones = Revision.objects.filter(
        version__planificacion=planificacion
    ).select_related('version', 'usuario').order_by('-fecha')

    context = {
        'planificacion': planificacion,
        'revisiones': revisiones,
    }
    return render(request, 'revisiones/historial.html', context)

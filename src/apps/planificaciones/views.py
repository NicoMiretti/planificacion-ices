"""
Vistas para el módulo de planificaciones.
CU-07 Cargar planificación, CU-08 Enviar, CU-14 Clonar.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse

from apps.usuarios.decorators import solo_profesor
from apps.catalogos.models import Materia, Plantilla
from apps.instancias.models import InstanciaPresentacion

from .models import Planificacion, Version
from .validators import validar_documento_word, nombre_campo
from .forms import SubirPlanificacionForm


@login_required
@solo_profesor
def cargar_planificacion(request, instancia_id, materia_id):
    """CU-07: Cargar planificación (subir archivo Word como borrador)."""
    instancia = get_object_or_404(InstanciaPresentacion, pk=instancia_id)
    materia = get_object_or_404(Materia, pk=materia_id)
    profesor = request.user.perfil_profesor

    # Verificar que el profesor es titular de la materia
    if materia.profesor_titular != profesor:
        messages.error(request, 'No eres el titular de esta materia.')
        return redirect('instancias:mis_instancias')

    # Obtener o crear la planificación
    planificacion, _ = Planificacion.objects.get_or_create(
        materia=materia,
        profesor=profesor,
        instancia=instancia
    )

    # Plantilla de la institución del profesor
    plantilla = Plantilla.vigente_para(profesor.institucion) if hasattr(Plantilla, 'vigente_para') else None

    if request.method == 'POST':
        form = SubirPlanificacionForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']

            version = Version(
                planificacion=planificacion,
                numero=planificacion.siguiente_numero_version(),
                archivo=archivo
            )
            version.save()

            messages.success(request, f'Borrador v{version.numero} guardado correctamente.')
            return redirect('planificaciones:detalle', pk=planificacion.pk)
    else:
        form = SubirPlanificacionForm()

    context = {
        'instancia': instancia,
        'materia': materia,
        'planificacion': planificacion,
        'plantilla': plantilla,
        'form': form,
        'versiones': planificacion.versiones.all(),
    }
    return render(request, 'planificaciones/cargar.html', context)


@login_required
@solo_profesor
def enviar_planificacion(request, version_id):
    """CU-08: Enviar planificación al circuito de revisión."""
    version = get_object_or_404(Version, pk=version_id)
    profesor = request.user.perfil_profesor

    # Verificar permisos
    if version.planificacion.profesor != profesor:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('instancias:mis_instancias')

    # Verificar estado
    if version.estado != Version.Estado.BORRADOR:
        messages.error(request, 'Esta versión ya fue enviada.')
        return redirect('planificaciones:detalle', pk=version.planificacion.pk)

    # Validar documento
    version.archivo.seek(0)
    es_valido, campos_faltantes = validar_documento_word(version.archivo)

    if not es_valido:
        version.rechazar_automaticamente(campos_faltantes)
        version.save()

        nombres_faltantes = [nombre_campo(c) for c in campos_faltantes]
        messages.error(
            request,
            f'El documento no cumple con los campos obligatorios. '
            f'Faltan: {", ".join(nombres_faltantes)}'
        )
    else:
        version.enviar()
        version.save()

        if version.entrega_tardia:
            messages.warning(
                request,
                f'Planificación enviada como ENTREGA TARDÍA ({version.dias_atraso} días de atraso).'
            )
        else:
            messages.success(request, 'Planificación enviada correctamente.')

    return redirect('planificaciones:detalle', pk=version.planificacion.pk)


@login_required
def detalle_planificacion(request, pk):
    """Detalle de una planificación con su historial de versiones."""
    planificacion = get_object_or_404(Planificacion, pk=pk)

    user = request.user
    if user.es_profesor:
        if planificacion.profesor.usuario != user:
            messages.error(request, 'No tienes acceso a esta planificación.')
            return redirect('instancias:mis_instancias')

    context = {
        'planificacion': planificacion,
        'versiones': planificacion.versiones.all(),
        'version_actual': planificacion.ultima_version,
        'nombre_campo': nombre_campo,
    }
    return render(request, 'planificaciones/detalle.html', context)


@login_required
def descargar_version(request, version_id):
    """Descargar archivo Word de una versión."""
    version = get_object_or_404(Version, pk=version_id)

    return FileResponse(
        version.archivo.open('rb'),
        as_attachment=True,
        filename=f"{version.planificacion.materia.nombre}_v{version.numero}.docx"
    )


@login_required
@solo_profesor
def clonar_oficial_previa(request, materia_id, instancia_id):
    """CU-14: Clonar planificación oficial de un período anterior."""
    materia = get_object_or_404(Materia, pk=materia_id)
    instancia_destino = get_object_or_404(InstanciaPresentacion, pk=instancia_id)
    profesor = request.user.perfil_profesor

    # Planificaciones oficiales anteriores de esta materia
    planif_anteriores = Planificacion.objects.filter(
        materia=materia,
        version_oficial__isnull=False
    ).exclude(
        instancia=instancia_destino
    ).order_by('-instancia__anio_academico')

    if request.method == 'POST':
        version_id = request.POST.get('version_id')
        version_origen = get_object_or_404(Version, pk=version_id)

        planif_destino, _ = Planificacion.objects.get_or_create(
            materia=materia,
            profesor=profesor,
            instancia=instancia_destino
        )

        # Copiar archivo
        from django.core.files.base import ContentFile
        version_origen.archivo.seek(0)
        contenido = version_origen.archivo.read()

        nueva_version = Version(
            planificacion=planif_destino,
            numero=planif_destino.siguiente_numero_version(),
        )
        nueva_version.archivo.save(
            f"clon_v{version_origen.numero}.docx",
            ContentFile(contenido)
        )
        nueva_version.save()

        messages.success(request, f'Planificación clonada como borrador v{nueva_version.numero}')
        return redirect('planificaciones:detalle', pk=planif_destino.pk)

    context = {
        'materia': materia,
        'instancia_destino': instancia_destino,
        'planificaciones_anteriores': planif_anteriores,
    }
    return render(request, 'planificaciones/clonar.html', context)

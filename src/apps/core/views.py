from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """Página principal con dashboard contextual por rol."""
    user = request.user
    context = {}

    if user.es_profesor and hasattr(user, 'perfil_profesor'):
        from apps.instancias.models import InstanciaPresentacion
        from apps.planificaciones.models import Planificacion, Version

        profesor = user.perfil_profesor
        instancias_qs = InstanciaPresentacion.objects.para_profesor(user)
        activas = instancias_qs.activas()

        # Planificaciones vigentes (en instancias activas)
        planifs = Planificacion.objects.filter(
            profesor=profesor,
            instancia__in=activas
        ).prefetch_related('versiones')

        stats = {
            'instancias_activas': activas.count(),
            'rechazadas': 0,
            'en_revision': 0,
            'borradores': 0,
            'oficiales': 0,
            'sin_cargar': 0,
        }
        alertas = []
        for p in planifs:
            ultima = p.versiones.order_by('-numero').first()
            if ultima is None:
                # Planificación asignada pero el profesor aún no subió nada
                stats['sin_cargar'] += 1
                alertas.append({
                    'tipo': 'warning',
                    'icono': 'bi-exclamation-triangle',
                    'texto': f'{p.materia.nombre} ({p.instancia.nombre} {p.instancia.anio_academico}): tenés que cargar tu planificación.',
                    'url': f'/instancias/{p.instancia.pk}/',
                })
            elif ultima.estado in ('rechazada', 'rechazada_auto'):
                stats['rechazadas'] += 1
                alertas.append({
                    'tipo': 'danger',
                    'icono': 'bi-x-circle-fill',
                    'texto': f'{p.materia.nombre}: planificación rechazada — necesita corrección.',
                    'url': f'/planificaciones/{p.pk}/',
                })
            elif ultima.estado == 'en_revision':
                stats['en_revision'] += 1
                alertas.append({
                    'tipo': 'warning',
                    'icono': 'bi-hourglass-split',
                    'texto': f'{p.materia.nombre}: en revisión.',
                    'url': f'/planificaciones/{p.pk}/',
                })
            elif ultima.estado == 'borrador':
                stats['borradores'] += 1
                alertas.append({
                    'tipo': 'secondary',
                    'icono': 'bi-file-earmark',
                    'texto': f'{p.materia.nombre}: borrador guardado, todavía no enviada.',
                    'url': f'/planificaciones/{p.pk}/',
                })
            elif ultima.estado in ('oficial', 'aprobada'):
                stats['oficiales'] += 1
        context['stats'] = stats
        context['alertas'] = alertas

    elif user.es_revisor:
        from apps.planificaciones.models import Version
        from apps.revisiones.models import VistoBueno
        from apps.instancias.models import InstanciaPresentacion
        from apps.catalogos.models import Carrera
        from django.db.models import Exists, OuterRef, Q

        versiones_qs = Version.objects.filter(
            estado__in=['en_revision']
        )
        if user.es_coordinador:
            mis_carreras = Carrera.objects.filter(coordinador=user).values_list('id', flat=True)
            versiones_qs = versiones_qs.filter(
                planificacion__materia__carrera_id__in=mis_carreras
            )

        total_pendientes = versiones_qs.count()
        esperando_mi_visto = versiones_qs.filter(
            estado='en_revision'
        ).exclude(
            Exists(VistoBueno.objects.filter(version=OuterRef('pk'), rol=user.rol))
        ).count()
        ya_di_visto = versiones_qs.filter(
            Exists(VistoBueno.objects.filter(version=OuterRef('pk'), rol=user.rol))
        ).count()
        tardias = versiones_qs.filter(entrega_tardia=True).count()

        instancias_abiertas = InstanciaPresentacion.objects.filter(estado='abierta').count()

        alertas = []
        if esperando_mi_visto:
            alertas.append({
                'tipo': 'warning',
                'icono': 'bi-hourglass-split',
                'texto': f'{esperando_mi_visto} planificación{"es" if esperando_mi_visto > 1 else ""} en revisión esperando tu aceptación.',
                'url': '/revisiones/',
            })
        if tardias:
            alertas.append({
                'tipo': 'danger',
                'icono': 'bi-clock-history',
                'texto': f'{tardias} planificación{"es" if tardias > 1 else ""} con entrega tardía.',
                'url': '/revisiones/?tardia=1',
            })

        context['stats'] = {
            'total_pendientes': total_pendientes,
            'esperando_mi_visto': esperando_mi_visto,
            'ya_di_visto': ya_di_visto,
            'tardias': tardias,
            'instancias_abiertas': instancias_abiertas,
        }
        context['alertas'] = alertas

    return render(request, 'core/home.html', context)

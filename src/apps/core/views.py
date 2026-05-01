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
            'enviadas': 0,
            'borradores': 0,
            'oficiales': 0,
        }
        alertas = []
        for p in planifs:
            ultima = p.versiones.order_by('-numero').first()
            if ultima:
                if ultima.estado in ('rechazada', 'rechazada_auto'):
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
                elif ultima.estado == 'enviada':
                    stats['enviadas'] += 1
                    alertas.append({
                        'tipo': 'info',
                        'icono': 'bi-send',
                        'texto': f'{p.materia.nombre}: enviada, esperando que un revisor la tome.',
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

        # Materias sin planificación en instancias abiertas
        from apps.catalogos.models import Materia
        pendientes_sin_planif = 0
        for inst in activas.filter(estado='abierta'):
            mats = inst.materias_audiencia().filter(profesor_titular=profesor)
            planif_ids = Planificacion.objects.filter(
                instancia=inst, profesor=profesor
            ).values_list('materia_id', flat=True)
            sin = mats.exclude(id__in=planif_ids).count()
            pendientes_sin_planif += sin
            if sin:
                alertas.append({
                    'tipo': 'warning',
                    'icono': 'bi-exclamation-triangle',
                    'texto': f'Instancia {inst.nombre} {inst.anio_academico}: tenés {sin} materia{"s" if sin > 1 else ""} sin planificación cargada.',
                    'url': f'/instancias/{inst.pk}/',
                })

        stats['sin_cargar'] = pendientes_sin_planif
        context['stats'] = stats
        context['alertas'] = alertas

    elif user.es_revisor:
        from apps.planificaciones.models import Version
        from apps.revisiones.models import VistoBueno
        from apps.instancias.models import InstanciaPresentacion
        from apps.catalogos.models import Carrera
        from django.db.models import Exists, OuterRef, Q

        versiones_qs = Version.objects.filter(
            estado__in=['enviada', 'en_revision']
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
        nuevas_enviadas = versiones_qs.filter(estado='enviada').count()

        instancias_abiertas = InstanciaPresentacion.objects.filter(estado='abierta').count()

        alertas = []
        if nuevas_enviadas:
            alertas.append({
                'tipo': 'info',
                'icono': 'bi-send',
                'texto': f'{nuevas_enviadas} planificación{"es" if nuevas_enviadas > 1 else ""} nueva{"s" if nuevas_enviadas > 1 else ""} esperando ser tomada{"s" if nuevas_enviadas > 1 else ""}.',
                'url': '/revisiones/',
            })
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
            'nuevas_enviadas': nuevas_enviadas,
            'esperando_mi_visto': esperando_mi_visto,
            'ya_di_visto': ya_di_visto,
            'tardias': tardias,
            'instancias_abiertas': instancias_abiertas,
        }
        context['alertas'] = alertas

    return render(request, 'core/home.html', context)

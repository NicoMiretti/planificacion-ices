"""
Servicio de revisión. Encapsula la lógica de negocio del circuito:
aprobar (doble visto), rechazar y corrección leve.
"""
from django.db import transaction

from apps.planificaciones.models import Version
from .models import Revision, VistoBueno


class RevisionService:
    """Lógica de revisión desacoplada de las vistas."""
    @staticmethod
    @transaction.atomic
    def aprobar(version, usuario):
        """
        Registra el visto bueno del usuario.
        Si ya existe aprobación del otro rol (moderadora + coordinador),
        marca la versión como APROBADA y luego OFICIAL.

        RN-03: Doble aprobación requerida.
        """
        if version.estado != Version.Estado.EN_REVISION:
            raise ValueError(f'Solo se pueden aprobar versiones en revisión (estado: {version.estado})')

        rol = usuario.rol
        if rol not in ['moderadora', 'coordinador']:
            raise ValueError('Solo moderadora o coordinador pueden aprobar')

        # El coordinador solo puede aprobar su propia carrera
        if rol == 'coordinador':
            carrera = version.planificacion.materia.carrera
            if carrera.coordinador != usuario:
                raise ValueError('No eres coordinador de esta carrera')

        # Registrar visto bueno (get_or_create para idempotencia)
        _, created = VistoBueno.objects.get_or_create(
            version=version,
            rol=rol,
            defaults={'usuario': usuario}
        )

        if not created:
            raise ValueError(f'Ya registraste tu visto bueno para esta versión')

        Revision.objects.create(
            planificacion=version.planificacion,
            version=version,
            usuario=usuario,
            tipo=Revision.Tipo.APROBAR,
            observaciones=f'Visto bueno de {rol}'
        )

        # Verificar si hay doble visto
        roles_aprobados = list(version.vistos_buenos.values_list('rol', flat=True))
        if 'moderadora' in roles_aprobados and 'coordinador' in roles_aprobados:
            version.aprobar()
            version.save()
            version.marcar_oficial()
            version.save()

        return version

    @staticmethod
    @transaction.atomic
    def rechazar(version, usuario, observaciones):
        """
        Rechaza la versión con observaciones obligatorias.
        El profesor deberá subir una nueva versión.
        """
        if version.estado != Version.Estado.EN_REVISION:
            raise ValueError(f'Solo se pueden rechazar versiones en revisión (estado: {version.estado})')

        if not observaciones or not observaciones.strip():
            raise ValueError('Las observaciones son obligatorias para rechazar')

        version.rechazar()
        version.save()

        Revision.objects.create(
            planificacion=version.planificacion,
            version=version,
            usuario=usuario,
            tipo=Revision.Tipo.RECHAZAR,
            observaciones=observaciones.strip()
        )

        return version

    @staticmethod
    @transaction.atomic
    def aplicar_correccion_leve(version, usuario, detalle, archivo_corregido=None):
        """
        La moderadora aplica una corrección menor sin devolver al profesor.
        La versión permanece en revisión.

        RN-07: Solo la moderadora puede aplicar correcciones leves.
        """
        if version.estado != Version.Estado.EN_REVISION:
            raise ValueError(f'Solo se pueden corregir versiones en revisión (estado: {version.estado})')

        if usuario.rol != 'moderadora':
            raise ValueError('Solo la moderadora puede aplicar correcciones leves')

        if not detalle or not detalle.strip():
            raise ValueError('El detalle de la corrección es obligatorio')

        revision = Revision.objects.create(
            planificacion=version.planificacion,
            version=version,
            usuario=usuario,
            tipo=Revision.Tipo.CORRECCION_LEVE,
            detalle_correccion=detalle.strip(),
            archivo_corregido=archivo_corregido
        )

        return revision

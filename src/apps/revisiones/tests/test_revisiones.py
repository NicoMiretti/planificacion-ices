"""
Tests para el módulo de revisiones.
Verifica: servicio de revisión, doble visto, rechazo, corrección leve y vistas.
Ejecutar: docker-compose exec web pytest apps/revisiones/tests/ -v
"""
import pytest
from datetime import date, timedelta

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.catalogos.models import Institucion, Carrera, Materia, Profesor
from apps.instancias.models import InstanciaPresentacion
from apps.planificaciones.models import Planificacion, Version
from apps.revisiones.models import Revision, VistoBueno
from apps.revisiones.services import RevisionService
from apps.usuarios.models import Usuario


# ============================================================
# Fixtures comunes
# ============================================================

@pytest.fixture
def institucion():
    return Institucion.objects.create(nombre='ICES Revisiones', codigo='ICR')


@pytest.fixture
def usuario_moderadora():
    return Usuario.objects.create_user(
        email='moderadora.rev@ices.edu',
        password='test123',
        rol=Usuario.Rol.MODERADORA,
        nombre_completo='Moderadora Rev'
    )


@pytest.fixture
def usuario_coordinador(db):
    return Usuario.objects.create_user(
        email='coordinador.rev@ices.edu',
        password='test123',
        rol=Usuario.Rol.COORDINADOR,
        nombre_completo='Coordinador Rev'
    )


@pytest.fixture
def carrera(institucion, usuario_coordinador):
    return Carrera.objects.create(
        nombre='Ingeniería en Sistemas Rev',
        institucion=institucion,
        coordinador=usuario_coordinador
    )


@pytest.fixture
def usuario_profesor():
    return Usuario.objects.create_user(
        email='prof.rev@ices.edu',
        password='test123',
        rol=Usuario.Rol.PROFESOR,
        nombre_completo='Profesor Rev'
    )


@pytest.fixture
def profesor(usuario_profesor, institucion):
    return Profesor.objects.create(
        usuario=usuario_profesor,
        institucion=institucion,
    )


@pytest.fixture
def materia(carrera, profesor):
    return Materia.objects.create(
        nombre='Análisis de Sistemas',
        carrera=carrera,
        anio_cursado=2,
        regimen=Materia.Regimen.ANUAL,
        profesor_titular=profesor
    )


@pytest.fixture
def instancia(carrera):
    inst = InstanciaPresentacion.objects.create(
        nombre='Planificaciones 2026 Rev',
        anio_academico=2026,
        periodo=InstanciaPresentacion.Periodo.ANUAL,
        fecha_apertura=date.today() - timedelta(days=5),
        fecha_limite=date.today() + timedelta(days=25),
    )
    inst.carreras.add(carrera)
    return inst


@pytest.fixture
def planificacion(materia, profesor, instancia):
    p, _ = Planificacion.objects.get_or_create(
        materia=materia,
        profesor=profesor,
        instancia=instancia
    )
    return p


@pytest.fixture
def version_en_revision(planificacion):
    """Versión ya en revisión (enviada va directo a EN_REVISION)."""
    archivo = SimpleUploadedFile('plan.docx', b'contenido')
    v = Version.objects.create(planificacion=planificacion, numero=1, archivo=archivo)
    v.enviar()
    v.save()
    return v


# ============================================================
# TESTS DEL SERVICIO — APROBAR (DOBLE VISTO)
# ============================================================

@pytest.mark.django_db
class TestAprobar:
    """Tests de doble aprobación (RN-03)."""

    def test_primer_visto_no_aprueba(self, version_en_revision, usuario_moderadora):
        """Un solo visto bueno no cambia el estado a APROBADA."""
        version = RevisionService.aprobar(version_en_revision, usuario_moderadora)
        version.refresh_from_db()
        assert version.estado == Version.Estado.EN_REVISION
        assert VistoBueno.objects.filter(version=version, rol='moderadora').exists()

    def test_doble_visto_aprueba_y_marca_oficial(
        self, version_en_revision, usuario_moderadora, usuario_coordinador
    ):
        """Con visto de moderadora + coordinador → OFICIAL. (RN-03)"""
        RevisionService.aprobar(version_en_revision, usuario_moderadora)
        version = RevisionService.aprobar(version_en_revision, usuario_coordinador)
        version.refresh_from_db()
        assert version.estado == Version.Estado.OFICIAL
        assert version.planificacion.version_oficial == version

    def test_no_se_puede_aprobar_dos_veces_mismo_rol(
        self, version_en_revision, usuario_moderadora
    ):
        """El mismo rol no puede aprobar dos veces."""
        RevisionService.aprobar(version_en_revision, usuario_moderadora)
        with pytest.raises(ValueError, match='Ya registraste tu visto bueno'):
            RevisionService.aprobar(version_en_revision, usuario_moderadora)

    def test_coordinador_incorrecto_no_puede_aprobar(
        self, version_en_revision
    ):
        """Coordinador de otra carrera no puede aprobar."""
        otro_coord = Usuario.objects.create_user(
            email='otro.coord@ices.edu',
            password='x',
            rol=Usuario.Rol.COORDINADOR
        )
        with pytest.raises(ValueError, match='No eres coordinador'):
            RevisionService.aprobar(version_en_revision, otro_coord)

    def test_profesor_no_puede_aprobar(self, version_en_revision, usuario_profesor):
        """Un profesor no puede dar visto bueno."""
        with pytest.raises(ValueError, match='Solo moderadora o coordinador'):
            RevisionService.aprobar(version_en_revision, usuario_profesor)


# ============================================================
# TESTS DEL SERVICIO — RECHAZAR
# ============================================================

@pytest.mark.django_db
class TestRechazar:
    """Tests de rechazar (CU-04)."""

    def test_rechazar_cambia_estado(
        self, version_en_revision, usuario_moderadora
    ):
        """Rechazar cambia estado a RECHAZADA."""
        version = RevisionService.rechazar(
            version_en_revision, usuario_moderadora, 'Falta la bibliografía completa'
        )
        version.refresh_from_db()
        assert version.estado == Version.Estado.RECHAZADA

    def test_rechazar_crea_revision_con_observaciones(
        self, version_en_revision, usuario_moderadora
    ):
        """El rechazo guarda las observaciones en Revision."""
        obs = 'Falta la bibliografía completa'
        RevisionService.rechazar(version_en_revision, usuario_moderadora, obs)
        revision = Revision.objects.get(
            version=version_en_revision,
            tipo=Revision.Tipo.RECHAZAR
        )
        assert revision.observaciones == obs

    def test_rechazar_sin_observaciones_falla(
        self, version_en_revision, usuario_moderadora
    ):
        """RN: Las observaciones son obligatorias para rechazar."""
        with pytest.raises(ValueError, match='obligatorias'):
            RevisionService.rechazar(version_en_revision, usuario_moderadora, '')

    def test_rechazar_observaciones_solo_espacios_falla(
        self, version_en_revision, usuario_moderadora
    ):
        """Observaciones con solo espacios también se rejectan."""
        with pytest.raises(ValueError, match='obligatorias'):
            RevisionService.rechazar(version_en_revision, usuario_moderadora, '   ')


# ============================================================
# TESTS DEL SERVICIO — CORRECCIÓN LEVE
# ============================================================

@pytest.mark.django_db
class TestCorreccionLeve:
    """Tests de corrección leve (CU-05, RN-07)."""

    def test_moderadora_puede_corregir(
        self, version_en_revision, usuario_moderadora
    ):
        """Moderadora puede aplicar corrección leve."""
        revision = RevisionService.aplicar_correccion_leve(
            version_en_revision, usuario_moderadora, 'Ajuste de formato en bibliografía'
        )
        assert revision.tipo == Revision.Tipo.CORRECCION_LEVE
        assert revision.detalle_correccion == 'Ajuste de formato en bibliografía'

    def test_corrección_no_cambia_estado(
        self, version_en_revision, usuario_moderadora
    ):
        """La corrección leve no cambia el estado de la versión."""
        RevisionService.aplicar_correccion_leve(
            version_en_revision, usuario_moderadora, 'Corrección menor'
        )
        version_en_revision.refresh_from_db()
        assert version_en_revision.estado == Version.Estado.EN_REVISION

    def test_coordinador_no_puede_corregir(
        self, version_en_revision, usuario_coordinador
    ):
        """RN-07: Solo la moderadora puede aplicar correcciones leves."""
        with pytest.raises(ValueError, match='Solo la moderadora'):
            RevisionService.aplicar_correccion_leve(
                version_en_revision, usuario_coordinador, 'Corrección'
            )

    def test_corrección_sin_detalle_falla(
        self, version_en_revision, usuario_moderadora
    ):
        """El detalle de la corrección es obligatorio."""
        with pytest.raises(ValueError, match='obligatorio'):
            RevisionService.aplicar_correccion_leve(
                version_en_revision, usuario_moderadora, ''
            )


# ============================================================
# TESTS DE VISTAS
# ============================================================

@pytest.mark.django_db
class TestRevisionesViews:
    """Tests de las vistas del módulo de revisiones."""

    def test_tablero_requiere_login(self):
        """Tablero redirige si no está autenticado."""
        client = Client()
        response = client.get('/revisiones/')
        assert response.status_code == 302

    def test_tablero_requiere_rol_revisor(self, usuario_profesor):
        """Tablero redirige a profesores (no son revisores)."""
        client = Client()
        client.force_login(usuario_profesor)
        response = client.get('/revisiones/')
        assert response.status_code in [302, 403]

    def test_tablero_accesible_moderadora(self, usuario_moderadora):
        """Moderadora puede acceder al tablero."""
        client = Client()
        client.force_login(usuario_moderadora)
        response = client.get('/revisiones/')
        assert response.status_code == 200

    def test_tablero_accesible_coordinador(self, usuario_coordinador):
        """Coordinador puede acceder al tablero."""
        client = Client()
        client.force_login(usuario_coordinador)
        response = client.get('/revisiones/')
        assert response.status_code == 200

    def test_aprobar_via_post(
        self, version_en_revision, usuario_moderadora
    ):
        """POST a aprobar registra visto bueno."""
        client = Client()
        client.force_login(usuario_moderadora)
        response = client.post(f'/revisiones/aprobar/{version_en_revision.pk}/')
        assert response.status_code == 302
        assert VistoBueno.objects.filter(
            version=version_en_revision, rol='moderadora'
        ).exists()

    def test_rechazar_via_post(
        self, version_en_revision, usuario_moderadora
    ):
        """POST a rechazar cambia estado a RECHAZADA."""
        client = Client()
        client.force_login(usuario_moderadora)
        response = client.post(
            f'/revisiones/rechazar/{version_en_revision.pk}/',
            {'observaciones': 'Falta fundamentación detallada'}
        )
        assert response.status_code == 302
        version_en_revision.refresh_from_db()
        assert version_en_revision.estado == Version.Estado.RECHAZADA

    def test_rechazar_sin_observaciones_no_cambia_estado(
        self, version_en_revision, usuario_moderadora
    ):
        """POST a rechazar sin observaciones no cambia el estado."""
        client = Client()
        client.force_login(usuario_moderadora)
        client.post(
            f'/revisiones/rechazar/{version_en_revision.pk}/',
            {'observaciones': ''}
        )
        version_en_revision.refresh_from_db()
        assert version_en_revision.estado == Version.Estado.EN_REVISION

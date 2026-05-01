"""
Tests para el módulo de instancias de presentación.
Verifica: modelo, manager, estados automáticos, audiencia.
"""
import pytest
from datetime import date, timedelta
from django.utils import timezone

from apps.instancias.models import InstanciaPresentacion
from apps.catalogos.models import Institucion, Carrera, Materia, Profesor
from apps.usuarios.models import Usuario


@pytest.fixture
def institucion():
    """Institución de prueba."""
    return Institucion.objects.create(nombre='ICES Test', codigo='ICES')


@pytest.fixture
def carrera(institucion):
    """Carrera de prueba."""
    return Carrera.objects.create(
        nombre='Ingeniería en Sistemas',
        institucion=institucion
    )


@pytest.fixture
def usuario_profesor():
    """Usuario con rol profesor."""
    return Usuario.objects.create_user(
        email='profesor.test@ices.edu',
        password='test123',
        rol=Usuario.Rol.PROFESOR,
        nombre_completo='Profesor Test'
    )


@pytest.fixture
def profesor(usuario_profesor, institucion):
    """Perfil de profesor."""
    return Profesor.objects.create(
        usuario=usuario_profesor,
        institucion=institucion,
        legajo='P-001'
    )


@pytest.fixture
def materia(carrera, profesor):
    """Materia de prueba asignada al profesor."""
    return Materia.objects.create(
        nombre='Programación I',
        carrera=carrera,
        anio_cursado=1,
        regimen=Materia.Regimen.PRIMER_CUATRIMESTRE,
        profesor_titular=profesor
    )


@pytest.fixture
def usuario_moderadora():
    """Usuario con rol moderadora."""
    return Usuario.objects.create_user(
        email='moderadora.test@ices.edu',
        password='test123',
        rol=Usuario.Rol.MODERADORA,
        nombre_completo='Moderadora Test'
    )


# ============================================================
# TESTS DE MODELO
# ============================================================

@pytest.mark.django_db
class TestInstanciaPresentacionModelo:
    """Tests para el modelo InstanciaPresentacion."""

    def test_crear_instancia_basica(self, carrera):
        """RF-06: Moderadora puede crear instancia de presentación."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Planificaciones 2026',
            anio_academico=2026,
            periodo=InstanciaPresentacion.Periodo.ANUAL,
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
        )
        instancia.carreras.add(carrera)
        
        assert instancia.pk is not None
        assert str(instancia) == 'Planificaciones 2026 (2026)'
        assert instancia.carreras.count() == 1

    def test_estado_programada_antes_apertura(self, carrera):
        """Estado debe ser 'programada' si la fecha de apertura es futura."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Programada',
            anio_academico=2026,
            periodo=InstanciaPresentacion.Periodo.ANUAL,
            fecha_apertura=date.today() + timedelta(days=10),
            fecha_limite=date.today() + timedelta(days=40),
        )
        instancia.carreras.add(carrera)
        
        assert instancia.estado == InstanciaPresentacion.Estado.PROGRAMADA

    def test_estado_abierta_entre_fechas(self, carrera):
        """Estado debe ser 'abierta' si estamos entre apertura y límite."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Abierta',
            anio_academico=2026,
            periodo=InstanciaPresentacion.Periodo.ANUAL,
            fecha_apertura=date.today() - timedelta(days=5),
            fecha_limite=date.today() + timedelta(days=25),
        )
        instancia.carreras.add(carrera)
        
        assert instancia.estado == InstanciaPresentacion.Estado.ABIERTA
        assert instancia.esta_abierta is True
        assert instancia.acepta_envios is True

    def test_estado_abierta_despues_limite(self, carrera):
        """Después del límite sigue abierta (acepta tardías)."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Tardía',
            anio_academico=2026,
            periodo=InstanciaPresentacion.Periodo.ANUAL,
            fecha_apertura=date.today() - timedelta(days=30),
            fecha_limite=date.today() - timedelta(days=5),
        )
        instancia.carreras.add(carrera)
        
        assert instancia.estado == InstanciaPresentacion.Estado.ABIERTA
        assert instancia.es_tardia is True

    def test_cerrada_manual_no_reabre(self, carrera):
        """Una instancia cerrada manualmente no se reabre automáticamente."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Cerrada',
            anio_academico=2026,
            periodo=InstanciaPresentacion.Periodo.ANUAL,
            fecha_apertura=date.today() - timedelta(days=5),
            fecha_limite=date.today() + timedelta(days=25),
            estado=InstanciaPresentacion.Estado.CERRADA,
        )
        instancia.carreras.add(carrera)
        
        # Guardar de nuevo - no debe cambiar estado
        instancia.save()
        assert instancia.estado == InstanciaPresentacion.Estado.CERRADA


# ============================================================
# TESTS DE AUDIENCIA
# ============================================================

@pytest.mark.django_db
class TestInstanciaAudiencia:
    """Tests para la funcionalidad de audiencia."""

    def test_materias_audiencia_por_carrera(self, carrera, materia):
        """RF-06: Audiencia incluye materias de las carreras seleccionadas."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Audiencia',
            anio_academico=2026,
            periodo=InstanciaPresentacion.Periodo.ANUAL,
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
        )
        instancia.carreras.add(carrera)
        
        materias = instancia.materias_audiencia()
        assert materia in materias

    def test_materias_audiencia_filtro_regimen(self, carrera, materia):
        """RF-06: Audiencia puede filtrar por régimen de materia."""
        # Crear materia anual
        materia_anual = Materia.objects.create(
            nombre='Proyecto Final',
            carrera=carrera,
            anio_cursado=4,
            regimen=Materia.Regimen.ANUAL,
        )
        
        # Instancia solo para cuatrimestrales
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Solo Cuatri',
            anio_academico=2026,
            periodo=InstanciaPresentacion.Periodo.PRIMER_CUATRIMESTRE,
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
            solo_regimen=Materia.Regimen.PRIMER_CUATRIMESTRE,
        )
        instancia.carreras.add(carrera)
        
        materias = instancia.materias_audiencia()
        assert materia in materias  # cuatrimestral
        assert materia_anual not in materias

    def test_materias_audiencia_filtro_institucion(self, institucion, carrera, materia):
        """RF-06: Audiencia puede filtrar por institución."""
        # Crear otra institución y carrera
        otra_inst = Institucion.objects.create(nombre='UCSE', codigo='UCSE')
        otra_carrera = Carrera.objects.create(nombre='Sistemas', institucion=otra_inst)
        otra_materia = Materia.objects.create(
            nombre='Prog I',
            carrera=otra_carrera,
            anio_cursado=1,
            regimen=Materia.Regimen.PRIMER_CUATRIMESTRE,
        )
        
        # Instancia solo para ICES
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Solo ICES',
            anio_academico=2026,
            periodo=InstanciaPresentacion.Periodo.ANUAL,
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
            institucion=institucion,
        )
        instancia.carreras.add(carrera, otra_carrera)
        
        materias = instancia.materias_audiencia()
        assert materia in materias
        assert otra_materia not in materias

    def test_profesores_audiencia(self, carrera, materia, profesor):
        """RF-06: Profesores de audiencia incluye a los titulares de materias."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Profesores',
            anio_academico=2026,
            periodo=InstanciaPresentacion.Periodo.ANUAL,
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
        )
        instancia.carreras.add(carrera)
        
        profesores = instancia.profesores_audiencia()
        assert profesor in profesores


# ============================================================
# TESTS DE MANAGER
# ============================================================

@pytest.mark.django_db
class TestInstanciaManager:
    """Tests para el InstanciaManager."""

    def test_manager_activas(self, carrera):
        """Manager.activas() retorna programadas y abiertas."""
        # Crear instancias en diferentes estados
        programada = InstanciaPresentacion.objects.create(
            nombre='Programada',
            anio_academico=2026,
            periodo='anual',
            fecha_apertura=date.today() + timedelta(days=10),
            fecha_limite=date.today() + timedelta(days=40),
        )
        programada.carreras.add(carrera)
        
        abierta = InstanciaPresentacion.objects.create(
            nombre='Abierta',
            anio_academico=2026,
            periodo='1cuat',
            fecha_apertura=date.today() - timedelta(days=5),
            fecha_limite=date.today() + timedelta(days=25),
        )
        abierta.carreras.add(carrera)
        
        cerrada = InstanciaPresentacion.objects.create(
            nombre='Cerrada',
            anio_academico=2025,
            periodo='anual',
            fecha_apertura=date.today() - timedelta(days=365),
            fecha_limite=date.today() - timedelta(days=300),
            estado=InstanciaPresentacion.Estado.CERRADA,
        )
        cerrada.carreras.add(carrera)
        
        activas = InstanciaPresentacion.objects.activas()
        assert programada in activas
        assert abierta in activas
        assert cerrada not in activas

    def test_manager_abiertas(self, carrera):
        """Manager.abiertas() solo retorna las abiertas."""
        abierta = InstanciaPresentacion.objects.create(
            nombre='Abierta',
            anio_academico=2026,
            periodo='anual',
            fecha_apertura=date.today() - timedelta(days=5),
            fecha_limite=date.today() + timedelta(days=25),
        )
        abierta.carreras.add(carrera)
        
        programada = InstanciaPresentacion.objects.create(
            nombre='Programada',
            anio_academico=2026,
            periodo='1cuat',
            fecha_apertura=date.today() + timedelta(days=10),
            fecha_limite=date.today() + timedelta(days=40),
        )
        programada.carreras.add(carrera)
        
        abiertas = InstanciaPresentacion.objects.abiertas()
        assert abierta in abiertas
        assert programada not in abiertas

    def test_manager_para_profesor(self, carrera, materia, usuario_profesor, profesor):
        """Manager.para_profesor() retorna instancias donde el profesor tiene materias."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test',
            anio_academico=2026,
            periodo='anual',
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
        )
        instancia.carreras.add(carrera)
        
        # Usuario tiene perfil_profesor con materia asignada
        instancias = InstanciaPresentacion.objects.para_profesor(usuario_profesor)
        assert instancia in instancias

    def test_manager_para_profesor_sin_perfil(self, carrera, usuario_moderadora):
        """Manager.para_profesor() retorna vacío si no tiene perfil de profesor."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test',
            anio_academico=2026,
            periodo='anual',
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
        )
        instancia.carreras.add(carrera)
        
        # Moderadora no tiene perfil_profesor
        instancias = InstanciaPresentacion.objects.para_profesor(usuario_moderadora)
        assert instancias.count() == 0


# ============================================================
# TESTS DE VISTAS
# ============================================================

@pytest.mark.django_db
class TestInstanciaViews:
    """Tests para las vistas de instancias."""

    def test_lista_instancias_requiere_moderadora(self, client, usuario_profesor):
        """Vista lista_instancias solo accesible para moderadora."""
        client.force_login(usuario_profesor)
        response = client.get('/instancias/')
        # Debe redirigir o denegar (depende del decorator)
        assert response.status_code in [302, 403]

    def test_lista_instancias_moderadora_accede(self, client, usuario_moderadora, carrera):
        """Moderadora puede acceder a lista de instancias."""
        # Crear instancia
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Lista',
            anio_academico=2026,
            periodo='anual',
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
        )
        instancia.carreras.add(carrera)
        
        client.force_login(usuario_moderadora)
        response = client.get('/instancias/')
        assert response.status_code == 200

    def test_mis_instancias_profesor(self, client, usuario_profesor, profesor, carrera, materia):
        """Profesor ve sus instancias asignadas."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Mis',
            anio_academico=2026,
            periodo='anual',
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
        )
        instancia.carreras.add(carrera)
        
        client.force_login(usuario_profesor)
        response = client.get('/instancias/mis/')
        assert response.status_code == 200

    def test_detalle_instancia(self, client, usuario_moderadora, carrera):
        """Cualquier usuario logueado puede ver detalle."""
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test Detalle',
            anio_academico=2026,
            periodo='anual',
            fecha_apertura=date.today(),
            fecha_limite=date.today() + timedelta(days=30),
        )
        instancia.carreras.add(carrera)
        
        client.force_login(usuario_moderadora)
        response = client.get(f'/instancias/{instancia.pk}/')
        assert response.status_code == 200

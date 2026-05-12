"""
Tests para app catalogos - Fase 2.
Ejecutar: docker-compose exec web pytest apps/catalogos/tests/ -v
"""
import pytest
from django.contrib.auth import get_user_model
from apps.catalogos.models import (
    Institucion, Carrera, Materia, Profesor, Plantilla, MaterialApoyo
)

User = get_user_model()


@pytest.fixture
def institucion_ices():
    """Fixture: Institución ICES."""
    return Institucion.objects.create(
        nombre='Instituto Cooperativo de Enseñanza Superior',
        codigo='ICES'
    )


@pytest.fixture
def institucion_ucse():
    """Fixture: Institución UCSE."""
    return Institucion.objects.create(
        nombre='Universidad Católica de Santiago del Estero',
        codigo='UCSE'
    )


@pytest.fixture
def coordinador(db):
    """Fixture: Usuario coordinador."""
    return User.objects.create_user(
        email='coordinador@ices.edu',
        password='test123',
        rol=User.Rol.COORDINADOR,
        nombre_completo='Juan Coordinador'
    )


@pytest.fixture
def usuario_profesor(db):
    """Fixture: Usuario con rol profesor."""
    return User.objects.create_user(
        email='profesor@ices.edu',
        password='test123',
        rol=User.Rol.PROFESOR,
        nombre_completo='María Profesora'
    )


@pytest.mark.django_db
class TestInstitucion:
    """Tests del modelo Institución."""

    def test_crear_institucion(self, institucion_ices):
        assert institucion_ices.codigo == 'ICES'
        assert str(institucion_ices) == 'ICES'

    def test_codigo_unico(self, institucion_ices):
        """No permite códigos duplicados."""
        with pytest.raises(Exception):
            Institucion.objects.create(nombre='Otro nombre', codigo='ICES')


@pytest.mark.django_db
class TestCarrera:
    """Tests del modelo Carrera."""

    def test_crear_carrera(self, institucion_ices, coordinador):
        carrera = Carrera.objects.create(
            nombre='Ingeniería en Sistemas',
            institucion=institucion_ices,
            coordinador=coordinador
        )
        
        assert carrera.nombre == 'Ingeniería en Sistemas'
        assert carrera.institucion == institucion_ices
        assert carrera.coordinador == coordinador
        assert carrera.activo is True  # default

    def test_carrera_str(self, institucion_ices):
        carrera = Carrera.objects.create(
            nombre='Contador Público',
            institucion=institucion_ices
        )
        assert str(carrera) == 'Contador Público (ICES)'

    def test_carrera_sin_coordinador(self, institucion_ices):
        """Carrera puede no tener coordinador asignado."""
        carrera = Carrera.objects.create(
            nombre='Abogacía',
            institucion=institucion_ices,
            coordinador=None
        )
        assert carrera.coordinador is None

    def test_nombre_unico_por_institucion(self, institucion_ices, institucion_ucse):
        """Mismo nombre permitido en distintas instituciones."""
        Carrera.objects.create(nombre='Sistemas', institucion=institucion_ices)
        
        # Mismo nombre en UCSE: OK
        carrera_ucse = Carrera.objects.create(nombre='Sistemas', institucion=institucion_ucse)
        assert carrera_ucse.institucion == institucion_ucse
        
        # Mismo nombre en ICES: ERROR
        with pytest.raises(Exception):
            Carrera.objects.create(nombre='Sistemas', institucion=institucion_ices)


@pytest.mark.django_db
class TestProfesor:
    """Tests del modelo Profesor."""

    def test_crear_profesor(self, institucion_ices, usuario_profesor):
        profesor = Profesor.objects.create(
            usuario=usuario_profesor,
            institucion=institucion_ices,
            legajo='12345'
        )
        
        assert profesor.usuario == usuario_profesor
        assert profesor.email == 'profesor@ices.edu'
        assert profesor.nombre == 'María Profesora'
        assert profesor.legajo == '12345'

    def test_profesor_str(self, institucion_ices, usuario_profesor):
        profesor = Profesor.objects.create(
            usuario=usuario_profesor,
            institucion=institucion_ices
        )
        assert str(profesor) == 'María Profesora'

    def test_un_profesor_por_usuario(self, institucion_ices, usuario_profesor):
        """Un usuario solo puede tener un perfil de profesor."""
        Profesor.objects.create(usuario=usuario_profesor, institucion=institucion_ices)
        
        with pytest.raises(Exception):
            Profesor.objects.create(usuario=usuario_profesor, institucion=institucion_ices)


@pytest.mark.django_db
class TestMateria:
    """Tests del modelo Materia."""

    @pytest.fixture
    def carrera(self, institucion_ices):
        return Carrera.objects.create(
            nombre='Ingeniería en Sistemas',
            institucion=institucion_ices
        )

    @pytest.fixture
    def profesor(self, institucion_ices, usuario_profesor):
        return Profesor.objects.create(
            usuario=usuario_profesor,
            institucion=institucion_ices
        )

    def test_crear_materia(self, carrera, profesor):
        materia = Materia.objects.create(
            nombre='Programación I',
            carrera=carrera,
            anio_cursado=1,
            regimen=Materia.Regimen.ANUAL,
            profesor_titular=profesor
        )
        
        assert materia.nombre == 'Programación I'
        assert materia.anio_cursado == 1
        assert materia.regimen == 'anual'
        assert materia.profesor_titular == profesor

    def test_materia_str(self, carrera):
        materia = Materia.objects.create(
            nombre='Base de Datos',
            carrera=carrera,
            anio_cursado=2,
            regimen=Materia.Regimen.PRIMER_CUATRIMESTRE
        )
        assert 'Base de Datos' in str(materia)
        assert '2° año' in str(materia)

    def test_materia_institucion(self, carrera, institucion_ices):
        """Materia hereda institución de la carrera."""
        materia = Materia.objects.create(
            nombre='Física',
            carrera=carrera,
            anio_cursado=1
        )
        assert materia.institucion == institucion_ices

    def test_regimenes_validos(self, carrera):
        """Verifica los regímenes válidos."""
        assert Materia.Regimen.ANUAL == 'anual'
        assert Materia.Regimen.PRIMER_CUATRIMESTRE == '1cuat'
        assert Materia.Regimen.SEGUNDO_CUATRIMESTRE == '2cuat'

    def test_materia_sin_profesor(self, carrera):
        """Materia puede no tener profesor asignado."""
        materia = Materia.objects.create(
            nombre='Electiva',
            carrera=carrera,
            anio_cursado=5,
            profesor_titular=None
        )
        assert materia.profesor_titular is None


@pytest.mark.django_db
class TestPlantilla:
    """Tests del modelo Plantilla."""

    def test_plantilla_vigente_para(self, institucion_ices):
        """Obtiene la plantilla activa más reciente."""
        from datetime import date
        
        # Plantilla vieja
        Plantilla.objects.create(
            institucion=institucion_ices,
            archivo='plantillas/ICES/vieja.docx',
            vigente_desde=date(2025, 1, 1),
            activo=True
        )
        
        # Plantilla nueva (debería ser la vigente)
        nueva = Plantilla.objects.create(
            institucion=institucion_ices,
            archivo='plantillas/ICES/nueva.docx',
            vigente_desde=date(2026, 1, 1),
            activo=True
        )
        
        vigente = Plantilla.vigente_para(institucion_ices)
        assert vigente == nueva

    def test_plantilla_inactiva_no_vigente(self, institucion_ices):
        """Plantilla inactiva no es considerada vigente."""
        from datetime import date
        
        Plantilla.objects.create(
            institucion=institucion_ices,
            archivo='plantillas/ICES/inactiva.docx',
            vigente_desde=date(2026, 1, 1),
            activo=False
        )
        
        activa = Plantilla.objects.create(
            institucion=institucion_ices,
            archivo='plantillas/ICES/activa.docx',
            vigente_desde=date(2025, 1, 1),
            activo=True
        )
        
        vigente = Plantilla.vigente_para(institucion_ices)
        assert vigente == activa


@pytest.mark.django_db
class TestMaterialApoyo:
    """Tests del modelo MaterialApoyo."""

    def test_crear_material(self):
        material = MaterialApoyo.objects.create(
            tipo=MaterialApoyo.Tipo.GUIA_APA,
            nombre='Guía APA 7ma edición',
            archivo='materiales/guia_apa/guia.pdf',
            anio_academico=2026
        )
        
        assert material.tipo == 'guia_apa'
        assert material.anio_academico == 2026
        assert str(material) == 'Guía APA 7ma edición (2026)'

    def test_tipos_validos(self):
        """Verifica los tipos válidos de material."""
        assert MaterialApoyo.Tipo.REGLAMENTO == 'reglamento'
        assert MaterialApoyo.Tipo.CALENDARIO == 'calendario'
        assert MaterialApoyo.Tipo.GUIA_APA == 'guia_apa'
        assert MaterialApoyo.Tipo.DOC_ORIENTADOR == 'doc_orientador'
        assert MaterialApoyo.Tipo.OTRO == 'otro'

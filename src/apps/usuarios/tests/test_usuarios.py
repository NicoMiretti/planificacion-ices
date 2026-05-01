"""
Tests para app usuarios - Fase 1.
Ejecutar: docker-compose exec web pytest apps/usuarios/tests/ -v
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUsuarioModel:
    """Tests del modelo Usuario."""

    def test_crear_usuario_con_email(self):
        """Puede crear usuario con email como identificador."""
        user = User.objects.create_user(
            email='profesor@ices.edu',
            password='testpass123'
        )
        assert user.email == 'profesor@ices.edu'
        assert user.check_password('testpass123')
        assert user.rol == User.Rol.PROFESOR  # default

    def test_crear_superusuario(self):
        """Superuser se crea con rol admin."""
        admin = User.objects.create_superuser(
            email='admin@ices.edu',
            password='adminpass123'
        )
        assert admin.is_superuser
        assert admin.is_staff
        assert admin.rol == User.Rol.ADMIN

    def test_email_unico(self):
        """No permite emails duplicados."""
        User.objects.create_user(email='test@ices.edu', password='pass123')
        
        with pytest.raises(Exception):  # IntegrityError
            User.objects.create_user(email='test@ices.edu', password='pass456')

    def test_email_obligatorio(self):
        """Email es obligatorio."""
        with pytest.raises(ValueError):
            User.objects.create_user(email='', password='pass123')


@pytest.mark.django_db
class TestUsuarioRoles:
    """Tests de los helpers de roles."""

    def test_es_admin(self):
        admin = User(rol=User.Rol.ADMIN)
        assert admin.es_admin
        assert not admin.es_profesor

    def test_es_moderadora(self):
        mod = User(rol=User.Rol.MODERADORA)
        assert mod.es_moderadora
        assert mod.es_revisor  # moderadora puede revisar
        assert not mod.es_profesor

    def test_es_coordinador(self):
        coord = User(rol=User.Rol.COORDINADOR)
        assert coord.es_coordinador
        assert coord.es_revisor  # coordinador puede revisar
        assert not coord.es_moderadora

    def test_es_profesor(self):
        prof = User(rol=User.Rol.PROFESOR)
        assert prof.es_profesor
        assert not prof.es_revisor  # profesor NO revisa

    def test_es_revisor(self):
        """Solo moderadora y coordinador son revisores."""
        mod = User(rol=User.Rol.MODERADORA)
        coord = User(rol=User.Rol.COORDINADOR)
        prof = User(rol=User.Rol.PROFESOR)
        alumno = User(rol=User.Rol.ALUMNO)
        
        assert mod.es_revisor
        assert coord.es_revisor
        assert not prof.es_revisor
        assert not alumno.es_revisor

    def test_es_consulta(self):
        """Alumno y gestión solo consultan."""
        alumno = User(rol=User.Rol.ALUMNO)
        gestion = User(rol=User.Rol.GESTION)
        prof = User(rol=User.Rol.PROFESOR)
        
        assert alumno.es_consulta
        assert gestion.es_consulta
        assert not prof.es_consulta

    def test_puede_gestionar(self):
        """Solo admin y moderadora pueden gestionar catálogos."""
        admin = User(rol=User.Rol.ADMIN)
        mod = User(rol=User.Rol.MODERADORA)
        coord = User(rol=User.Rol.COORDINADOR)
        
        assert admin.puede_gestionar
        assert mod.puede_gestionar
        assert not coord.puede_gestionar


@pytest.mark.django_db
class TestUsuarioAuth:
    """Tests de autenticación."""

    def test_login_con_email(self, client):
        """Puede loguearse con email."""
        User.objects.create_user(
            email='test@ices.edu',
            password='testpass123'
        )
        
        response = client.post('/usuarios/login/', {
            'username': 'test@ices.edu',  # Django usa 'username' en el form
            'password': 'testpass123'
        })
        
        # Si login exitoso, redirige (302)
        assert response.status_code == 302

    def test_login_fallido(self, client):
        """Login fallido no redirige."""
        User.objects.create_user(
            email='test@ices.edu',
            password='testpass123'
        )
        
        response = client.post('/usuarios/login/', {
            'username': 'test@ices.edu',
            'password': 'wrongpassword'
        })
        
        # Si falla, muestra el form de nuevo (200)
        assert response.status_code == 200

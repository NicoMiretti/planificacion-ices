"""
Modelo de usuario personalizado con autenticación por email y roles.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UsuarioManager(BaseUserManager):
    """Manager para Usuario con email como identificador."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', Usuario.Rol.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Usuario personalizado con email como username y sistema de roles.
    """
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        MODERADORA = 'moderadora', 'Moderadora (Sec. Académica)'
        COORDINADOR = 'coordinador', 'Coordinador'
        PROFESOR = 'profesor', 'Profesor'
        ALUMNO = 'alumno', 'Alumno'
        GESTION = 'gestion', 'Gestión / Secretaría'

    # Remover username, usar email
    username = None
    email = models.EmailField('email', unique=True)
    
    # Rol del usuario
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.PROFESOR,
        verbose_name='rol'
    )
    
    # Datos adicionales
    nombre_completo = models.CharField(max_length=200, blank=True, verbose_name='nombre completo')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        ordering = ['email']

    def __str__(self):
        return self.nombre_completo or self.email

    # === Helpers de rol ===
    
    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.is_superuser

    @property
    def es_moderadora(self):
        return self.rol == self.Rol.MODERADORA

    @property
    def es_coordinador(self):
        return self.rol == self.Rol.COORDINADOR

    @property
    def es_profesor(self):
        return self.rol == self.Rol.PROFESOR

    @property
    def es_revisor(self):
        """Puede revisar planificaciones (moderadora o coordinador)"""
        return self.rol in [self.Rol.MODERADORA, self.Rol.COORDINADOR]

    @property
    def es_consulta(self):
        """Solo puede consultar oficiales"""
        return self.rol in [self.Rol.ALUMNO, self.Rol.GESTION]
    
    @property
    def puede_gestionar(self):
        """Puede gestionar catálogos y configuración"""
        return self.rol in [self.Rol.ADMIN, self.Rol.MODERADORA] or self.is_superuser

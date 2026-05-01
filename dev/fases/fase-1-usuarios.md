# Fase 1 — Usuarios y Autenticación

> Duración estimada: 3-4 horas

## Objetivo

Sistema de usuarios con roles diferenciados y autenticación por email.

---

## Checklist

- [ ] Modelo `Usuario` custom con email como username
- [ ] Enum de roles
- [ ] Migración inicial
- [ ] Admin para gestionar usuarios
- [ ] Login/logout views
- [ ] Middleware/decorator para verificar roles
- [ ] Tests básicos

---

## Modelo

```python
# apps/usuarios/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UsuarioManager(BaseUserManager):
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
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        MODERADORA = 'moderadora', 'Moderadora (Sec. Académica)'
        COORDINADOR = 'coordinador', 'Coordinador'
        PROFESOR = 'profesor', 'Profesor'
        ALUMNO = 'alumno', 'Alumno'
        GESTION = 'gestion', 'Gestión / Secretaría'

    username = None  # Removemos username
    email = models.EmailField('email', unique=True)
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.PROFESOR
    )
    
    # Campos adicionales
    nombre_completo = models.CharField(max_length=200, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.email

    # Helpers para verificar rol
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
        """Puede revisar planificaciones"""
        return self.rol in [self.Rol.MODERADORA, self.Rol.COORDINADOR]

    @property
    def es_consulta(self):
        """Puede consultar oficiales"""
        return self.rol in [self.Rol.ALUMNO, self.Rol.GESTION]
```

---

## Admin

```python
# apps/usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nombre_completo', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff')
    search_fields = ('email', 'nombre_completo')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre_completo',)}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'rol', 'nombre_completo'),
        }),
    )
```

---

## Decoradores para Roles

```python
# apps/usuarios/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def rol_requerido(*roles_permitidos):
    """
    Decorator para restringir acceso por rol.
    
    Uso:
        @rol_requerido('moderadora', 'coordinador')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.rol not in roles_permitidos and not request.user.is_superuser:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Shortcuts
def solo_moderadora(view_func):
    return rol_requerido('moderadora')(view_func)


def solo_profesor(view_func):
    return rol_requerido('profesor')(view_func)


def revisores(view_func):
    return rol_requerido('moderadora', 'coordinador')(view_func)
```

---

## Mixin para Class-Based Views

```python
# apps/usuarios/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class RolRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    roles_permitidos = []

    def test_func(self):
        user = self.request.user
        return user.rol in self.roles_permitidos or user.is_superuser


class ModeradoraMixin(RolRequeridoMixin):
    roles_permitidos = ['moderadora']


class RevisorMixin(RolRequeridoMixin):
    roles_permitidos = ['moderadora', 'coordinador']


class ProfesorMixin(RolRequeridoMixin):
    roles_permitidos = ['profesor']
```

---

## URLs y Views de Auth

```python
# apps/usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='usuarios/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='usuarios:login'
    ), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
]
```

```python
# apps/usuarios/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')
```

---

## Template Login

```html
<!-- templates/usuarios/login.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h4>Iniciar Sesión</h4>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        <div class="mb-3">
                            <label for="username" class="form-label">Email</label>
                            <input type="email" name="username" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Contraseña</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Ingresar</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## Tests

```python
# apps/usuarios/tests/test_models.py
import pytest
from apps.usuarios.models import Usuario


@pytest.mark.django_db
class TestUsuario:
    def test_crear_usuario(self):
        user = Usuario.objects.create_user(
            email='profesor@ices.edu',
            password='test1234',
            rol=Usuario.Rol.PROFESOR
        )
        assert user.email == 'profesor@ices.edu'
        assert user.es_profesor
        assert not user.es_moderadora

    def test_crear_superuser(self):
        admin = Usuario.objects.create_superuser(
            email='admin@ices.edu',
            password='admin1234'
        )
        assert admin.is_superuser
        assert admin.es_admin

    def test_roles_helpers(self):
        mod = Usuario(rol=Usuario.Rol.MODERADORA)
        assert mod.es_moderadora
        assert mod.es_revisor
        assert not mod.es_profesor
```

---

## Verificación

```bash
# Crear migración
python manage.py makemigrations usuarios

# Aplicar
python manage.py migrate

# Crear superuser
python manage.py createsuperuser
# Email: admin@ices.edu
# Password: ****

# Correr tests
pytest apps/usuarios/tests/ -v

# Verificar en admin que puedes crear usuarios con distintos roles
```

✅ **Fase 1 completa cuando**: Puedes loguearte con distintos roles y el decorador `@rol_requerido` funciona.

---

## Siguiente: [Fase 2 - Catálogos](fase-2-catalogos.md)

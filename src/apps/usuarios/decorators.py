"""
Decoradores para control de acceso por rol.
"""
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
                return redirect('usuarios:login')
            if request.user.rol not in roles_permitidos and not request.user.is_superuser:
                raise PermissionDenied("No tienes permiso para acceder a esta página.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Shortcuts para roles comunes
def solo_moderadora(view_func):
    """Solo permite acceso a la moderadora."""
    return rol_requerido('moderadora', 'admin')(view_func)


def solo_profesor(view_func):
    """Solo permite acceso a profesores."""
    return rol_requerido('profesor')(view_func)


def revisores(view_func):
    """Permite acceso a moderadora y coordinadores."""
    return rol_requerido('moderadora', 'coordinador', 'admin')(view_func)


def gestores(view_func):
    """Permite acceso a quienes pueden gestionar catálogos."""
    return rol_requerido('moderadora', 'admin')(view_func)

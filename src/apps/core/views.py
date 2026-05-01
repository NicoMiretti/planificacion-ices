from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home(request):
    """
    Página principal - redirige según rol del usuario.
    """
    if not request.user.is_authenticated:
        return redirect('usuarios:login')
    
    user = request.user
    
    # Redirigir según rol
    if user.rol in ['moderadora', 'admin']:
        return redirect('revisiones:tablero')
    elif user.rol == 'coordinador':
        return redirect('revisiones:tablero')
    elif user.rol == 'profesor':
        return redirect('instancias:mis_instancias')
    elif user.rol in ['alumno', 'gestion']:
        return redirect('planificaciones:consulta_publica')
    
    return render(request, 'core/home.html')

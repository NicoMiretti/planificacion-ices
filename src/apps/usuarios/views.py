from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def perfil(request):
    """Vista del perfil del usuario."""
    return render(request, 'usuarios/perfil.html')

from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.usuarios.decorators import revisores as solo_revisores

app_name = 'revisiones'


@login_required
@solo_revisores
def tablero(request):
    """Placeholder - tablero de revisión."""
    return render(request, 'revisiones/tablero.html', {
        'mensaje': 'Esta funcionalidad se implementará en Fase 5.'
    })


urlpatterns = [
    path('', tablero, name='tablero'),
]

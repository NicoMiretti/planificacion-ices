from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

app_name = 'planificaciones'


@login_required
def consulta_publica(request):
    """Placeholder - consulta pública de planificaciones oficiales."""
    return render(request, 'planificaciones/consulta_publica.html', {
        'mensaje': 'Esta funcionalidad se implementará en Fase 6.'
    })


urlpatterns = [
    path('consulta/', consulta_publica, name='consulta_publica'),
]

from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

app_name = 'instancias'


@login_required
def mis_instancias(request):
    """Placeholder - se implementará en Fase 3."""
    return render(request, 'instancias/mis_instancias.html', {
        'mensaje': 'Esta funcionalidad se implementará en Fase 3.'
    })


urlpatterns = [
    path('mis/', mis_instancias, name='mis_instancias'),
]

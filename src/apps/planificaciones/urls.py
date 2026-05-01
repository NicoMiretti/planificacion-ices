from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'planificaciones'


@login_required
def consulta_publica(request):
    """Consulta pública de planificaciones oficiales (Fase 6)."""
    return render(request, 'planificaciones/consulta_publica.html', {})


urlpatterns = [
    path('cargar/<int:instancia_id>/<int:materia_id>/', views.cargar_planificacion, name='cargar'),
    path('enviar/<int:version_id>/', views.enviar_planificacion, name='enviar'),
    path('<int:pk>/', views.detalle_planificacion, name='detalle'),
    path('descargar/<int:version_id>/', views.descargar_version, name='descargar'),
    path('clonar/<int:materia_id>/<int:instancia_id>/', views.clonar_oficial_previa, name='clonar'),
    path('consulta/', consulta_publica, name='consulta_publica'),
]

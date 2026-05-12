from django.urls import path
from . import views

app_name = 'planificaciones'

urlpatterns = [
    path('cargar/<int:instancia_id>/<int:materia_id>/', views.cargar_planificacion, name='cargar'),
    path('enviar/<int:version_id>/', views.enviar_planificacion, name='enviar'),
    path('<int:pk>/', views.detalle_planificacion, name='detalle'),
    path('descargar/<int:version_id>/', views.descargar_version, name='descargar'),
    path('clonar/<int:materia_id>/<int:instancia_id>/', views.clonar_oficial_previa, name='clonar'),
]

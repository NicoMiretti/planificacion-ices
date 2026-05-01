from django.urls import path
from . import views

app_name = 'revisiones'

urlpatterns = [
    path('', views.tablero_revision, name='tablero'),
    path('revisar/<int:version_id>/', views.revisar_version, name='revisar'),
    path('aprobar/<int:version_id>/', views.aprobar_version, name='aprobar'),
    path('rechazar/<int:version_id>/', views.rechazar_version, name='rechazar'),
    path('correccion/<int:version_id>/', views.correccion_leve, name='correccion'),
    path('historial/<int:planificacion_id>/', views.historial_revisiones, name='historial'),
]

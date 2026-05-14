from django.urls import path
from . import views

app_name = 'instancias'

urlpatterns = [
    path('', views.lista_instancias, name='lista'),
    path('nueva/', views.crear_instancia, name='crear'),
    path('mis/', views.mis_instancias, name='mis_instancias'),
    path('<int:pk>/', views.detalle_instancia, name='detalle'),
    path('<int:pk>/editar/', views.editar_instancia, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_instancia, name='eliminar'),
    path('<int:pk>/preview/', views.ajax_preview_edicion, name='ajax_preview'),
    path('ajax/anios/', views.ajax_anios_por_carreras, name='ajax_anios'),
]

from django.urls import path
from . import views

app_name = 'instancias'

urlpatterns = [
    path('', views.lista_instancias, name='lista'),
    path('mis/', views.mis_instancias, name='mis_instancias'),
    path('<int:pk>/', views.detalle_instancia, name='detalle'),
]

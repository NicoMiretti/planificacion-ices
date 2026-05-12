from django.urls import path
from apps.catalogos import views

app_name = 'catalogos'

urlpatterns = [
    # Hub de catálogo
    path('', views.catalogo_home, name='catalogo'),

    # Instituciones
    path('instituciones/', views.institucion_lista, name='institucion_lista'),
    path('instituciones/nueva/', views.institucion_crear, name='institucion_crear'),
    path('instituciones/<int:pk>/editar/', views.institucion_editar, name='institucion_editar'),
    path('instituciones/<int:pk>/eliminar/', views.institucion_eliminar, name='institucion_eliminar'),

    # Carreras
    path('carreras/', views.carrera_lista, name='carrera_lista'),
    path('carreras/nueva/', views.carrera_crear, name='carrera_crear'),
    path('carreras/<int:pk>/editar/', views.carrera_editar, name='carrera_editar'),
    path('carreras/<int:pk>/eliminar/', views.carrera_eliminar, name='carrera_eliminar'),

    # Profesores
    path('profesores/', views.profesor_lista, name='profesor_lista'),
    path('profesores/nuevo/', views.profesor_crear, name='profesor_crear'),
    path('profesores/<int:pk>/editar/', views.profesor_editar, name='profesor_editar'),
    path('profesores/<int:pk>/eliminar/', views.profesor_eliminar, name='profesor_eliminar'),

    # Materias
    path('materias/', views.materia_lista, name='materia_lista'),
    path('materias/nueva/', views.materia_crear, name='materia_crear'),
    path('materias/<int:pk>/editar/', views.materia_editar, name='materia_editar'),
    path('materias/<int:pk>/eliminar/', views.materia_eliminar, name='materia_eliminar'),

    # Coordinadores
    path('coordinadores/', views.coordinador_lista, name='coordinador_lista'),
    path('coordinadores/nuevo/', views.coordinador_crear, name='coordinador_crear'),
    path('coordinadores/<int:pk>/editar/', views.coordinador_editar, name='coordinador_editar'),
    path('coordinadores/<int:pk>/eliminar/', views.coordinador_eliminar, name='coordinador_eliminar'),
]

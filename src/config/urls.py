"""
URL configuration for planificaciones project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Apps
    path('', include('apps.core.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('catalogos/', include('apps.catalogos.urls')),
    path('instancias/', include('apps.instancias.urls')),
    path('planificaciones/', include('apps.planificaciones.urls')),
    path('revisiones/', include('apps.revisiones.urls')),
]

# Media files en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Admin site customization
admin.site.site_header = 'Planificaciones ICES/UCSE'
admin.site.site_title = 'Planificaciones Admin'
admin.site.index_title = 'Administración del Sistema'

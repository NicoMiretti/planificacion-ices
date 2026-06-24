"""
URL configuration for planificaciones project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),

    # Apps
    path('', include('apps.core.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('catalogos/', include('apps.catalogos.urls')),
    path('instancias/', include('apps.instancias.urls')),
    path('planificaciones/', include('apps.planificaciones.urls')),
    path('revisiones/', include('apps.revisiones.urls')),
]

# Media files: siempre activo (en dev DEBUG lo resuelve también; en producción
# detrás de nginx con sub-path, path_info ya viene sin el prefijo SCRIPT_NAME,
# por eso el patrón usa '/media/' directamente).
from django.views.static import serve as _serve
from django.urls import re_path as _re_path
urlpatterns += [
    _re_path(r'^media/(?P<path>.*)$', _serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
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

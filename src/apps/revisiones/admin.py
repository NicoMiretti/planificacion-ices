from django.contrib import admin
from .models import Revision, VistoBueno


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'usuario', 'version', 'fecha')
    list_filter = ('tipo',)
    readonly_fields = ('fecha',)
    search_fields = ('version__planificacion__materia__nombre', 'usuario__email')


@admin.register(VistoBueno)
class VistoBuenoAdmin(admin.ModelAdmin):
    list_display = ('version', 'rol', 'usuario', 'fecha')
    list_filter = ('rol',)
    readonly_fields = ('fecha',)

from django.contrib import admin
from .models import Planificacion, Version


class VersionInline(admin.TabularInline):
    model = Version
    extra = 0
    readonly_fields = ('numero', 'estado', 'fecha_creacion', 'fecha_envio', 'entrega_tardia', 'dias_atraso', 'campos_faltantes')
    fields = ('numero', 'estado', 'fecha_envio', 'entrega_tardia', 'dias_atraso', 'campos_faltantes')


@admin.register(Planificacion)
class PlanificacionAdmin(admin.ModelAdmin):
    list_display = ('materia', 'profesor', 'instancia', 'tiene_oficial', 'cantidad_versiones', 'fecha_creacion')
    list_filter = ('instancia__anio_academico', 'instancia', 'materia__carrera')
    search_fields = ('materia__nombre', 'profesor__usuario__email')
    inlines = [VersionInline]
    readonly_fields = ('version_oficial', 'fecha_creacion')

    @admin.display(description='¿Tiene oficial?', boolean=True)
    def tiene_oficial(self, obj):
        return obj.tiene_oficial

    @admin.display(description='Versiones')
    def cantidad_versiones(self, obj):
        return obj.versiones.count()


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'estado', 'entrega_tardia', 'dias_atraso', 'fecha_envio')
    list_filter = ('estado', 'entrega_tardia')
    readonly_fields = ('estado', 'fecha_creacion', 'fecha_envio', 'fecha_aprobacion', 'entrega_tardia', 'dias_atraso', 'campos_faltantes')

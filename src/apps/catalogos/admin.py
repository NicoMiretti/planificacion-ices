from django.contrib import admin
from .models import Institucion, Carrera, Materia, Profesor, Plantilla, MaterialApoyo


@admin.register(Institucion)
class InstitucionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('nombre', 'codigo')


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'institucion', 'coordinador', 'activo')
    list_filter = ('institucion', 'activo')
    search_fields = ('nombre',)
    autocomplete_fields = ('coordinador',)


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'institucion', 'activo')
    list_filter = ('institucion', 'activo')
    search_fields = ('usuario__email', 'usuario__nombre_completo')
    autocomplete_fields = ('usuario',)
    
    def email(self, obj):
        return obj.usuario.email
    email.short_description = 'Email'


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'carrera', 'anio_cursado', 'regimen', 'profesor_titular', 'activo')
    list_filter = ('carrera__institucion', 'carrera', 'anio_cursado', 'regimen', 'activo')
    search_fields = ('nombre', 'profesor_titular__usuario__nombre_completo')
    autocomplete_fields = ('profesor_titular',)
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'carrera', 'anio_cursado', 'regimen')
        }),
        ('Asignación', {
            'fields': ('profesor_titular',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(Plantilla)
class PlantillaAdmin(admin.ModelAdmin):
    list_display = ('institucion', 'descripcion', 'vigente_desde', 'activo', 'fecha_creacion')
    list_filter = ('institucion', 'activo')
    date_hierarchy = 'vigente_desde'


@admin.register(MaterialApoyo)
class MaterialApoyoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'anio_academico', 'activo')
    list_filter = ('tipo', 'anio_academico', 'activo')
    search_fields = ('nombre', 'descripcion')

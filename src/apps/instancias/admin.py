from django.contrib import admin
from .models import InstanciaPresentacion


@admin.register(InstanciaPresentacion)
class InstanciaPresentacionAdmin(admin.ModelAdmin):
    """Admin para gestionar instancias de presentación."""
    
    list_display = (
        'nombre', 
        'anio_academico', 
        'periodo_display', 
        'fecha_apertura', 
        'fecha_limite', 
        'estado',
        'cantidad_carreras',
    )
    list_filter = ('anio_academico', 'periodo', 'estado', 'institucion')
    search_fields = ('nombre',)
    filter_horizontal = ('carreras',)  # Widget más amigable para M2M
    date_hierarchy = 'fecha_apertura'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'anio_academico', 'periodo')
        }),
        ('Audiencia', {
            'fields': ('carreras', 'institucion', 'solo_regimen'),
            'description': 'Define qué materias/profesores deben presentar'
        }),
        ('Fechas', {
            'fields': ('fecha_apertura', 'fecha_limite')
        }),
        ('Estado', {
            'fields': ('estado',),
            'description': 'Se actualiza automáticamente según fechas. '
                         'Marcar como "Cerrada" cierra manualmente.'
        }),
    )
    
    readonly_fields = ('creada_por', 'fecha_creacion')

    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='Período')
    def periodo_display(self, obj):
        return obj.get_periodo_display()

    @admin.display(description='Carreras')
    def cantidad_carreras(self, obj):
        return obj.carreras.count()

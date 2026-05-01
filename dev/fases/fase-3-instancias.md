# Fase 3 — Instancias de Presentación

> Duración estimada: 4-5 horas

## Objetivo

Permitir a la moderadora crear instancias de presentación con audiencia y fechas configurables.

---

## Checklist

- [ ] Modelo `InstanciaPresentacion`
- [ ] Relación M2M con Carrera (audiencia)
- [ ] Estados: programada, abierta, cerrada
- [ ] Transición automática por fecha
- [ ] Admin para crear instancias
- [ ] Vista para moderadora: listar instancias
- [ ] Vista para profesor: ver sus instancias asignadas
- [ ] Tests

---

## Modelos

```python
# apps/instancias/models.py
from django.db import models
from django.utils import timezone
from apps.catalogos.models import Carrera, Materia, Institucion


class InstanciaPresentacion(models.Model):
    class Periodo(models.TextChoices):
        ANUAL = 'anual', 'Anual'
        PRIMER_CUATRIMESTRE = '1cuat', '1° Cuatrimestre'
        SEGUNDO_CUATRIMESTRE = '2cuat', '2° Cuatrimestre'

    class Estado(models.TextChoices):
        PROGRAMADA = 'programada', 'Programada'
        ABIERTA = 'abierta', 'Abierta'
        CERRADA = 'cerrada', 'Cerrada'

    nombre = models.CharField(
        max_length=200,
        help_text='Ej: "Planificaciones Anuales 2026"'
    )
    anio_academico = models.PositiveSmallIntegerField(
        help_text='Año académico (ej: 2026)'
    )
    periodo = models.CharField(
        max_length=10,
        choices=Periodo.choices
    )
    
    # Audiencia: a qué carreras aplica
    carreras = models.ManyToManyField(
        Carrera,
        related_name='instancias',
        help_text='Carreras incluidas en esta instancia'
    )
    
    # Filtros adicionales de audiencia
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        null=True, blank=True,
        help_text='Filtrar por institución (vacío = todas)'
    )
    solo_regimen = models.CharField(
        max_length=10,
        choices=Materia.Regimen.choices,
        blank=True,
        help_text='Filtrar materias por régimen (vacío = todos)'
    )
    
    # Fechas
    fecha_apertura = models.DateField()
    fecha_limite = models.DateField()
    
    # Estado
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PROGRAMADA
    )
    
    # Metadata
    creada_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-anio_academico', '-fecha_apertura']
        verbose_name = 'instancia de presentación'
        verbose_name_plural = 'instancias de presentación'

    def __str__(self):
        return f"{self.nombre} ({self.anio_academico})"

    def save(self, *args, **kwargs):
        # Auto-actualizar estado según fechas
        self._actualizar_estado()
        super().save(*args, **kwargs)

    def _actualizar_estado(self):
        hoy = timezone.now().date()
        if self.estado != self.Estado.CERRADA:  # No reabrir cerradas manualmente
            if hoy < self.fecha_apertura:
                self.estado = self.Estado.PROGRAMADA
            elif hoy <= self.fecha_limite:
                self.estado = self.Estado.ABIERTA
            else:
                # Pasó la fecha límite pero sigue aceptando tardías
                self.estado = self.Estado.ABIERTA  # O CERRADA según política

    @property
    def esta_abierta(self):
        return self.estado == self.Estado.ABIERTA

    @property
    def acepta_envios(self):
        """Acepta envíos aunque sea después del límite (tardías)"""
        return self.estado in [self.Estado.ABIERTA]

    def materias_audiencia(self):
        """
        Retorna las materias que deben presentar en esta instancia.
        Filtra por carreras + régimen si aplica.
        """
        materias = Materia.objects.filter(
            carrera__in=self.carreras.all(),
            activa=True
        )
        
        # Filtrar por régimen si está especificado
        if self.solo_regimen:
            materias = materias.filter(regimen=self.solo_regimen)
        
        # Filtrar por institución si está especificado
        if self.institucion:
            materias = materias.filter(carrera__institucion=self.institucion)
        
        return materias.select_related('carrera', 'profesor_titular')

    def profesores_audiencia(self):
        """Profesores que deben presentar en esta instancia"""
        from apps.catalogos.models import Profesor
        materias = self.materias_audiencia()
        profesor_ids = materias.values_list('profesor_titular_id', flat=True).distinct()
        return Profesor.objects.filter(id__in=profesor_ids, activo=True)
```

---

## Manager con métodos útiles

```python
# apps/instancias/managers.py
from django.db import models
from django.utils import timezone


class InstanciaManager(models.Manager):
    def activas(self):
        """Instancias que aceptan envíos"""
        return self.filter(estado__in=['programada', 'abierta'])

    def abiertas(self):
        """Instancias actualmente abiertas"""
        return self.filter(estado='abierta')

    def del_anio(self, anio):
        """Instancias de un año académico específico"""
        return self.filter(anio_academico=anio)

    def historicas(self):
        """Instancias de años anteriores"""
        anio_actual = timezone.now().year
        return self.filter(anio_academico__lt=anio_actual)

    def para_profesor(self, profesor):
        """Instancias donde el profesor tiene materias asignadas"""
        from apps.catalogos.models import Materia
        carreras_profesor = Materia.objects.filter(
            profesor_titular__usuario=profesor,
            activa=True
        ).values_list('carrera_id', flat=True)
        
        return self.filter(carreras__id__in=carreras_profesor).distinct()


# En el modelo, agregar:
# objects = InstanciaManager()
```

---

## Admin

```python
# apps/instancias/admin.py
from django.contrib import admin
from .models import InstanciaPresentacion


@admin.register(InstanciaPresentacion)
class InstanciaPresentacionAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'anio_academico', 'periodo', 
        'fecha_apertura', 'fecha_limite', 'estado'
    )
    list_filter = ('anio_academico', 'periodo', 'estado', 'institucion')
    search_fields = ('nombre',)
    filter_horizontal = ('carreras',)  # Widget más amigable para M2M
    
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
            'description': 'Se actualiza automáticamente según fechas'
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)
```

---

## Views

```python
# apps/instancias/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.usuarios.decorators import rol_requerido, solo_moderadora
from .models import InstanciaPresentacion


@login_required
@solo_moderadora
def lista_instancias(request):
    """Vista para moderadora: todas las instancias"""
    instancias = InstanciaPresentacion.objects.all()
    
    # Filtros opcionales
    anio = request.GET.get('anio')
    if anio:
        instancias = instancias.filter(anio_academico=anio)
    
    estado = request.GET.get('estado')
    if estado:
        instancias = instancias.filter(estado=estado)
    
    context = {
        'instancias': instancias,
        'anios_disponibles': InstanciaPresentacion.objects.values_list(
            'anio_academico', flat=True
        ).distinct().order_by('-anio_academico'),
    }
    return render(request, 'instancias/lista.html', context)


@login_required
def mis_instancias(request):
    """Vista para profesor: sus instancias asignadas"""
    if not hasattr(request.user, 'perfil_profesor'):
        # No es profesor
        return render(request, 'instancias/no_profesor.html')
    
    profesor = request.user.perfil_profesor
    instancias = InstanciaPresentacion.objects.para_profesor(request.user)
    
    # Agrupar por estado
    context = {
        'instancias_activas': instancias.activas(),
        'instancias_historicas': instancias.historicas(),
        'profesor': profesor,
    }
    return render(request, 'instancias/mis_instancias.html', context)


@login_required
def detalle_instancia(request, pk):
    """Detalle de una instancia con sus materias"""
    instancia = get_object_or_404(InstanciaPresentacion, pk=pk)
    
    materias = instancia.materias_audiencia()
    
    # Si es profesor, filtrar solo sus materias
    if request.user.es_profesor and hasattr(request.user, 'perfil_profesor'):
        materias = materias.filter(profesor_titular=request.user.perfil_profesor)
    
    context = {
        'instancia': instancia,
        'materias': materias,
    }
    return render(request, 'instancias/detalle.html', context)
```

---

## URLs

```python
# apps/instancias/urls.py
from django.urls import path
from . import views

app_name = 'instancias'

urlpatterns = [
    path('', views.lista_instancias, name='lista'),
    path('mis/', views.mis_instancias, name='mis_instancias'),
    path('<int:pk>/', views.detalle_instancia, name='detalle'),
]
```

---

## Templates

```html
<!-- templates/instancias/mis_instancias.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h2>Mis Instancias de Presentación</h2>
    
    {% if instancias_activas %}
    <h4 class="mt-4">Instancias Activas</h4>
    <div class="list-group">
        {% for inst in instancias_activas %}
        <a href="{% url 'instancias:detalle' inst.pk %}" class="list-group-item list-group-item-action">
            <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">{{ inst.nombre }}</h5>
                <span class="badge bg-{{ inst.estado|estado_color }}">{{ inst.get_estado_display }}</span>
            </div>
            <p class="mb-1">Período: {{ inst.get_periodo_display }} {{ inst.anio_academico }}</p>
            <small>
                Fecha límite: {{ inst.fecha_limite|date:"d/m/Y" }}
                {% if inst.fecha_limite < today %}
                    <span class="text-danger">(Vencida - entregas tardías)</span>
                {% endif %}
            </small>
        </a>
        {% endfor %}
    </div>
    {% else %}
    <div class="alert alert-info">No hay instancias activas actualmente.</div>
    {% endif %}
    
    {% if instancias_historicas %}
    <h4 class="mt-4">Histórico</h4>
    <div class="list-group">
        {% for inst in instancias_historicas %}
        <a href="{% url 'instancias:detalle' inst.pk %}" class="list-group-item list-group-item-action">
            {{ inst.nombre }} ({{ inst.anio_academico }})
        </a>
        {% endfor %}
    </div>
    {% endif %}
</div>
{% endblock %}
```

---

## Comando para actualizar estados

```python
# apps/instancias/management/commands/actualizar_estados_instancias.py
from django.core.management.base import BaseCommand
from apps.instancias.models import InstanciaPresentacion


class Command(BaseCommand):
    help = 'Actualiza estados de instancias según fechas actuales'

    def handle(self, *args, **options):
        # Solo las que no están cerradas manualmente
        instancias = InstanciaPresentacion.objects.exclude(
            estado=InstanciaPresentacion.Estado.CERRADA
        )
        
        actualizadas = 0
        for inst in instancias:
            estado_anterior = inst.estado
            inst.save()  # Trigger _actualizar_estado()
            if inst.estado != estado_anterior:
                actualizadas += 1
                self.stdout.write(
                    f"{inst.nombre}: {estado_anterior} -> {inst.estado}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'{actualizadas} instancias actualizadas')
        )
```

Configurar como **cron job diario** o usar **Celery Beat**.

---

## Tests

```python
# apps/instancias/tests/test_models.py
import pytest
from datetime import date, timedelta
from apps.instancias.models import InstanciaPresentacion
from apps.catalogos.models import Institucion, Carrera


@pytest.mark.django_db
class TestInstancia:
    @pytest.fixture
    def setup(self):
        inst = Institucion.objects.create(nombre='ICES', codigo='ICES')
        carrera = Carrera.objects.create(nombre='Sistemas', institucion=inst)
        return inst, carrera

    def test_estado_programada(self, setup):
        _, carrera = setup
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test',
            anio_academico=2026,
            periodo='anual',
            fecha_apertura=date.today() + timedelta(days=10),
            fecha_limite=date.today() + timedelta(days=40),
        )
        instancia.carreras.add(carrera)
        assert instancia.estado == 'programada'

    def test_estado_abierta(self, setup):
        _, carrera = setup
        instancia = InstanciaPresentacion.objects.create(
            nombre='Test',
            anio_academico=2026,
            periodo='anual',
            fecha_apertura=date.today() - timedelta(days=5),
            fecha_limite=date.today() + timedelta(days=25),
        )
        instancia.carreras.add(carrera)
        assert instancia.estado == 'abierta'
```

---

## Verificación

```bash
# Migraciones
python manage.py makemigrations instancias
python manage.py migrate

# Tests
pytest apps/instancias/tests/ -v

# Crear instancia de prueba desde admin
# Verificar que las materias de las carreras seleccionadas aparecen
```

✅ **Fase 3 completa cuando**: Puedes crear una instancia con audiencia y un profesor ve sus instancias asignadas.

---

## Siguiente: [Fase 4 - Planificaciones](fase-4-planificaciones.md)

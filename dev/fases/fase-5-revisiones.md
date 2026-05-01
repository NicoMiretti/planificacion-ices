# Fase 5 — Revisiones (Moderadora + Coordinador)

> Duración estimada: 5-6 horas

## Objetivo

Tablero de revisión para moderadora/coordinador, con flujo de aprobación doble, rechazo con observaciones, y corrección leve.

---

## Checklist

- [ ] Modelo `Revision` (registra cada acción de revisión)
- [ ] Modelo `VistoBueno` (para doble aprobación)
- [ ] Tablero de planificaciones pendientes
- [ ] Vista de revisión individual
- [ ] Acciones: aprobar, rechazar, corrección leve
- [ ] Lógica de doble visto (moderadora + coordinador)
- [ ] Notificación al profesor (preparar para Fase 7)
- [ ] Tests

---

## Modelos

```python
# apps/revisiones/models.py
from django.db import models
from django.conf import settings


class Revision(models.Model):
    """Registra cada acción de revisión sobre una versión"""
    class Tipo(models.TextChoices):
        TOMAR = 'tomar', 'Tomar para revisión'
        APROBAR = 'aprobar', 'Aprobar'
        RECHAZAR = 'rechazar', 'Rechazar'
        CORRECCION_LEVE = 'correccion_leve', 'Corrección leve'

    version = models.ForeignKey(
        'planificaciones.Version',
        on_delete=models.CASCADE,
        related_name='revisiones'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    observaciones = models.TextField(blank=True)
    
    # Para corrección leve: qué se corrigió
    detalle_correccion = models.TextField(
        blank=True,
        help_text='Descripción de la corrección aplicada'
    )
    archivo_corregido = models.FileField(
        upload_to='correcciones/',
        null=True, blank=True,
        help_text='Documento con la corrección (opcional)'
    )
    
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'revisión'
        verbose_name_plural = 'revisiones'

    def __str__(self):
        return f"{self.get_tipo_display()} por {self.usuario} - {self.version}"


class VistoBueno(models.Model):
    """
    Registra la aprobación de un revisor específico.
    Se necesitan 2 (moderadora + coordinador) para aprobar.
    """
    version = models.ForeignKey(
        'planificaciones.Version',
        on_delete=models.CASCADE,
        related_name='vistos_buenos'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    rol = models.CharField(max_length=20)  # 'moderadora' o 'coordinador'
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('version', 'rol')
        verbose_name = 'visto bueno'
        verbose_name_plural = 'vistos buenos'

    def __str__(self):
        return f"VºBº {self.rol} - {self.version}"
```

---

## Services (lógica de negocio)

```python
# apps/revisiones/services.py
from django.db import transaction
from django.utils import timezone
from .models import Revision, VistoBueno
from apps.planificaciones.models import Version


class RevisionService:
    """Encapsula la lógica de revisión"""

    @staticmethod
    def tomar_para_revision(version, usuario):
        """Un revisor toma una planificación enviada"""
        if version.estado != Version.Estado.ENVIADA:
            raise ValueError(f'Estado inválido: {version.estado}')
        
        version.tomar_revision()
        version.save()
        
        Revision.objects.create(
            version=version,
            usuario=usuario,
            tipo=Revision.Tipo.TOMAR
        )
        return version

    @staticmethod
    @transaction.atomic
    def aprobar(version, usuario):
        """
        Registra aprobación del usuario.
        Si ya hay aprobación del otro rol, marca como aprobada.
        """
        if version.estado != Version.Estado.EN_REVISION:
            raise ValueError(f'Estado inválido: {version.estado}')
        
        rol = usuario.rol
        if rol not in ['moderadora', 'coordinador']:
            raise ValueError('Solo moderadora o coordinador pueden aprobar')
        
        # Verificar si el coordinador corresponde a la carrera
        if rol == 'coordinador':
            carrera = version.planificacion.materia.carrera
            if carrera.coordinador != usuario:
                raise ValueError('No eres coordinador de esta carrera')
        
        # Crear visto bueno
        visto, created = VistoBueno.objects.get_or_create(
            version=version,
            rol=rol,
            defaults={'usuario': usuario}
        )
        
        if not created:
            raise ValueError(f'Ya existe aprobación de {rol}')
        
        # Registrar revisión
        Revision.objects.create(
            version=version,
            usuario=usuario,
            tipo=Revision.Tipo.APROBAR,
            observaciones=f'Visto bueno de {rol}'
        )
        
        # Verificar si hay doble visto
        vistos = version.vistos_buenos.values_list('rol', flat=True)
        if 'moderadora' in vistos and 'coordinador' in vistos:
            # ¡Doble aprobación!
            version.aprobar()
            version.save()
            
            # Marcar como oficial
            version.marcar_oficial()
            version.save()
            
            # TODO: Notificar al profesor
        
        return version

    @staticmethod
    @transaction.atomic
    def rechazar(version, usuario, observaciones):
        """Rechaza con observaciones"""
        if version.estado != Version.Estado.EN_REVISION:
            raise ValueError(f'Estado inválido: {version.estado}')
        
        if not observaciones.strip():
            raise ValueError('Las observaciones son obligatorias')
        
        version.rechazar()
        version.save()
        
        Revision.objects.create(
            version=version,
            usuario=usuario,
            tipo=Revision.Tipo.RECHAZAR,
            observaciones=observaciones
        )
        
        # TODO: Notificar al profesor
        
        return version

    @staticmethod
    @transaction.atomic
    def aplicar_correccion_leve(version, usuario, detalle, archivo_corregido=None):
        """Moderadora aplica corrección sin devolver al profesor"""
        if version.estado != Version.Estado.EN_REVISION:
            raise ValueError(f'Estado inválido: {version.estado}')
        
        if usuario.rol != 'moderadora':
            raise ValueError('Solo la moderadora puede aplicar correcciones leves')
        
        revision = Revision.objects.create(
            version=version,
            usuario=usuario,
            tipo=Revision.Tipo.CORRECCION_LEVE,
            detalle_correccion=detalle,
            archivo_corregido=archivo_corregido
        )
        
        # La versión sigue en revisión, no cambia de estado
        # TODO: Notificar al profesor
        
        return revision
```

---

## Views

```python
# apps/revisiones/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Exists, OuterRef
from apps.usuarios.decorators import revisores
from apps.planificaciones.models import Planificacion, Version
from apps.catalogos.models import Carrera
from .models import Revision, VistoBueno
from .services import RevisionService
from .forms import RechazarForm, CorreccionLeveForm


@login_required
@revisores
def tablero_revision(request):
    """CU-02: Tablero de planificaciones para revisión"""
    user = request.user
    
    # Base: versiones enviadas o en revisión
    versiones = Version.objects.filter(
        estado__in=[Version.Estado.ENVIADA, Version.Estado.EN_REVISION]
    ).select_related(
        'planificacion__materia__carrera__institucion',
        'planificacion__profesor__usuario',
        'planificacion__instancia'
    )
    
    # Si es coordinador, filtrar solo sus carreras
    if user.es_coordinador:
        carreras_ids = Carrera.objects.filter(
            coordinador=user
        ).values_list('id', flat=True)
        versiones = versiones.filter(
            planificacion__materia__carrera_id__in=carreras_ids
        )
    
    # Anotar si ya tiene visto del usuario actual
    versiones = versiones.annotate(
        tiene_mi_visto=Exists(
            VistoBueno.objects.filter(
                version=OuterRef('pk'),
                rol=user.rol
            )
        )
    )
    
    # Filtros del request
    filtros = {}
    
    carrera_id = request.GET.get('carrera')
    if carrera_id:
        versiones = versiones.filter(planificacion__materia__carrera_id=carrera_id)
        filtros['carrera'] = carrera_id
    
    estado = request.GET.get('estado')
    if estado:
        versiones = versiones.filter(estado=estado)
        filtros['estado'] = estado
    
    instancia_id = request.GET.get('instancia')
    if instancia_id:
        versiones = versiones.filter(planificacion__instancia_id=instancia_id)
        filtros['instancia'] = instancia_id
    
    tardia = request.GET.get('tardia')
    if tardia == '1':
        versiones = versiones.filter(entrega_tardia=True)
        filtros['tardia'] = '1'
    
    # Ordenar: primero las más antiguas sin tomar
    versiones = versiones.order_by('estado', 'fecha_envio')
    
    # Datos para filtros
    context = {
        'versiones': versiones,
        'filtros': filtros,
        'carreras': Carrera.objects.filter(activa=True),
        'estados': [
            ('enviada', 'Enviada'),
            ('en_revision', 'En Revisión'),
        ],
    }
    return render(request, 'revisiones/tablero.html', context)


@login_required
@revisores
def revisar_version(request, version_id):
    """Vista de revisión individual"""
    version = get_object_or_404(
        Version.objects.select_related(
            'planificacion__materia__carrera',
            'planificacion__profesor__usuario',
            'planificacion__instancia'
        ),
        pk=version_id
    )
    
    user = request.user
    
    # Si está enviada y no en revisión, tomarla
    if version.estado == Version.Estado.ENVIADA:
        try:
            RevisionService.tomar_para_revision(version, user)
            messages.info(request, 'Planificación tomada para revisión.')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('revisiones:tablero')
    
    # Verificar permisos
    if user.es_coordinador:
        carrera = version.planificacion.materia.carrera
        if carrera.coordinador != user:
            messages.error(request, 'No tienes acceso a esta planificación.')
            return redirect('revisiones:tablero')
    
    # Verificar si ya tengo visto
    mi_visto = VistoBueno.objects.filter(
        version=version, rol=user.rol
    ).first()
    
    # Visto del otro rol
    otro_rol = 'coordinador' if user.rol == 'moderadora' else 'moderadora'
    otro_visto = VistoBueno.objects.filter(
        version=version, rol=otro_rol
    ).first()
    
    context = {
        'version': version,
        'planificacion': version.planificacion,
        'revisiones': version.revisiones.all(),
        'mi_visto': mi_visto,
        'otro_visto': otro_visto,
        'form_rechazo': RechazarForm(),
        'form_correccion': CorreccionLeveForm() if user.es_moderadora else None,
    }
    return render(request, 'revisiones/revisar.html', context)


@login_required
@revisores
def aprobar_version(request, version_id):
    """CU-03: Aprobar planificación"""
    if request.method != 'POST':
        return redirect('revisiones:revisar', version_id=version_id)
    
    version = get_object_or_404(Version, pk=version_id)
    
    try:
        RevisionService.aprobar(version, request.user)
        
        # Verificar si quedó oficial (doble visto)
        version.refresh_from_db()
        if version.estado == Version.Estado.OFICIAL:
            messages.success(request, '¡Planificación APROBADA y marcada como OFICIAL!')
        else:
            messages.success(request, f'Visto bueno registrado. Falta aprobación del otro revisor.')
        
    except ValueError as e:
        messages.error(request, str(e))
    
    return redirect('revisiones:tablero')


@login_required
@revisores
def rechazar_version(request, version_id):
    """CU-04: Rechazar planificación"""
    if request.method != 'POST':
        return redirect('revisiones:revisar', version_id=version_id)
    
    version = get_object_or_404(Version, pk=version_id)
    form = RechazarForm(request.POST)
    
    if form.is_valid():
        try:
            RevisionService.rechazar(
                version, 
                request.user, 
                form.cleaned_data['observaciones']
            )
            messages.success(request, 'Planificación rechazada. El profesor será notificado.')
        except ValueError as e:
            messages.error(request, str(e))
    else:
        messages.error(request, 'Las observaciones son obligatorias.')
    
    return redirect('revisiones:tablero')


@login_required
def correccion_leve(request, version_id):
    """CU-05: Aplicar corrección leve (solo moderadora)"""
    if request.method != 'POST':
        return redirect('revisiones:revisar', version_id=version_id)
    
    if not request.user.es_moderadora:
        messages.error(request, 'Solo la moderadora puede aplicar correcciones leves.')
        return redirect('revisiones:tablero')
    
    version = get_object_or_404(Version, pk=version_id)
    form = CorreccionLeveForm(request.POST, request.FILES)
    
    if form.is_valid():
        try:
            RevisionService.aplicar_correccion_leve(
                version,
                request.user,
                form.cleaned_data['detalle'],
                form.cleaned_data.get('archivo_corregido')
            )
            messages.success(request, 'Corrección aplicada y registrada.')
        except ValueError as e:
            messages.error(request, str(e))
    else:
        messages.error(request, 'Debes indicar el detalle de la corrección.')
    
    return redirect('revisiones:revisar', version_id=version_id)


@login_required
@revisores
def historial_revisiones(request, planificacion_id):
    """Ver historial completo de revisiones (para CU-09)"""
    planificacion = get_object_or_404(Planificacion, pk=planificacion_id)
    
    revisiones = Revision.objects.filter(
        version__planificacion=planificacion
    ).select_related('version', 'usuario').order_by('-fecha')
    
    context = {
        'planificacion': planificacion,
        'revisiones': revisiones,
    }
    return render(request, 'revisiones/historial.html', context)
```

---

## Forms

```python
# apps/revisiones/forms.py
from django import forms


class RechazarForm(forms.Form):
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Indica qué debe corregir el profesor...'
        }),
        label='Observaciones',
        required=True
    )


class CorreccionLeveForm(forms.Form):
    detalle = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Describe qué corregiste...'
        }),
        label='Detalle de la corrección',
        required=True
    )
    archivo_corregido = forms.FileField(
        label='Documento corregido (opcional)',
        required=False
    )
```

---

## URLs

```python
# apps/revisiones/urls.py
from django.urls import path
from . import views

app_name = 'revisiones'

urlpatterns = [
    path('', views.tablero_revision, name='tablero'),
    path('revisar/<int:version_id>/', views.revisar_version, name='revisar'),
    path('aprobar/<int:version_id>/', views.aprobar_version, name='aprobar'),
    path('rechazar/<int:version_id>/', views.rechazar_version, name='rechazar'),
    path('correccion/<int:version_id>/', views.correccion_leve, name='correccion'),
    path('historial/<int:planificacion_id>/', views.historial_revisiones, name='historial'),
]
```

---

## Template del Tablero

```html
<!-- templates/revisiones/tablero.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container-fluid mt-4">
    <h2>Tablero de Revisión</h2>
    
    <!-- Filtros -->
    <form method="get" class="row g-3 mb-4">
        <div class="col-md-3">
            <select name="carrera" class="form-select">
                <option value="">Todas las carreras</option>
                {% for c in carreras %}
                <option value="{{ c.id }}" {% if filtros.carrera == c.id|stringformat:"s" %}selected{% endif %}>
                    {{ c.nombre }}
                </option>
                {% endfor %}
            </select>
        </div>
        <div class="col-md-2">
            <select name="estado" class="form-select">
                <option value="">Todos los estados</option>
                {% for val, label in estados %}
                <option value="{{ val }}" {% if filtros.estado == val %}selected{% endif %}>
                    {{ label }}
                </option>
                {% endfor %}
            </select>
        </div>
        <div class="col-md-2">
            <div class="form-check mt-2">
                <input type="checkbox" name="tardia" value="1" class="form-check-input" 
                       {% if filtros.tardia %}checked{% endif %}>
                <label class="form-check-label">Solo tardías</label>
            </div>
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-outline-primary">Filtrar</button>
        </div>
    </form>

    <!-- Tabla de versiones -->
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Materia</th>
                <th>Profesor</th>
                <th>Carrera</th>
                <th>Instancia</th>
                <th>Versión</th>
                <th>Estado</th>
                <th>Tardía</th>
                <th>Fecha Envío</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for v in versiones %}
            <tr class="{% if v.tiene_mi_visto %}table-success{% endif %}">
                <td>{{ v.planificacion.materia.nombre }}</td>
                <td>{{ v.planificacion.profesor }}</td>
                <td>{{ v.planificacion.materia.carrera.nombre }}</td>
                <td>{{ v.planificacion.instancia.nombre }}</td>
                <td>v{{ v.numero }}</td>
                <td>
                    <span class="badge bg-{{ v.estado|estado_badge }}">
                        {{ v.get_estado_display }}
                    </span>
                    {% if v.tiene_mi_visto %}
                    <span class="badge bg-success">Mi VºBº</span>
                    {% endif %}
                </td>
                <td>
                    {% if v.entrega_tardia %}
                    <span class="badge bg-warning">{{ v.dias_atraso }}d</span>
                    {% else %}
                    -
                    {% endif %}
                </td>
                <td>{{ v.fecha_envio|date:"d/m/Y H:i" }}</td>
                <td>
                    <a href="{% url 'revisiones:revisar' v.pk %}" class="btn btn-sm btn-primary">
                        Revisar
                    </a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="9" class="text-center">No hay planificaciones pendientes de revisión.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

---

## Template de Revisión

```html
<!-- templates/revisiones/revisar.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <h3>{{ planificacion.materia.nombre }}</h3>
            <p class="text-muted">
                {{ planificacion.profesor }} | 
                {{ planificacion.materia.carrera.nombre }} |
                v{{ version.numero }}
            </p>
            
            <!-- Descargar documento -->
            <div class="mb-4">
                <a href="{% url 'planificaciones:descargar' version.pk %}" class="btn btn-outline-primary btn-lg">
                    📄 Descargar Documento Word
                </a>
                {% if version.entrega_tardia %}
                <span class="badge bg-warning ms-3">Entrega Tardía ({{ version.dias_atraso }} días)</span>
                {% endif %}
            </div>
            
            <!-- Estado de aprobaciones -->
            <div class="card mb-4">
                <div class="card-header">Estado de Aprobación</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-6">
                            <strong>Moderadora:</strong>
                            {% if otro_visto and otro_visto.rol == 'moderadora' or mi_visto and mi_visto.rol == 'moderadora' %}
                            <span class="badge bg-success">✓ Aprobado</span>
                            {% else %}
                            <span class="badge bg-secondary">Pendiente</span>
                            {% endif %}
                        </div>
                        <div class="col-6">
                            <strong>Coordinador:</strong>
                            {% if otro_visto and otro_visto.rol == 'coordinador' or mi_visto and mi_visto.rol == 'coordinador' %}
                            <span class="badge bg-success">✓ Aprobado</span>
                            {% else %}
                            <span class="badge bg-secondary">Pendiente</span>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Historial de revisiones -->
            <h5>Historial de Revisiones</h5>
            <ul class="list-group mb-4">
                {% for r in revisiones %}
                <li class="list-group-item">
                    <strong>{{ r.get_tipo_display }}</strong> por {{ r.usuario }}
                    <small class="text-muted float-end">{{ r.fecha|date:"d/m/Y H:i" }}</small>
                    {% if r.observaciones %}
                    <p class="mb-0 mt-2">{{ r.observaciones }}</p>
                    {% endif %}
                </li>
                {% empty %}
                <li class="list-group-item text-muted">Sin revisiones aún.</li>
                {% endfor %}
            </ul>
        </div>
        
        <div class="col-md-4">
            <!-- Acciones -->
            {% if not mi_visto and version.estado == 'en_revision' %}
            <div class="card mb-3">
                <div class="card-header bg-success text-white">Aprobar</div>
                <div class="card-body">
                    <form method="post" action="{% url 'revisiones:aprobar' version.pk %}">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-success w-100">
                            ✓ Dar Visto Bueno
                        </button>
                    </form>
                </div>
            </div>
            
            <div class="card mb-3">
                <div class="card-header bg-danger text-white">Rechazar</div>
                <div class="card-body">
                    <form method="post" action="{% url 'revisiones:rechazar' version.pk %}">
                        {% csrf_token %}
                        {{ form_rechazo.observaciones }}
                        <button type="submit" class="btn btn-danger w-100 mt-2">
                            ✗ Rechazar
                        </button>
                    </form>
                </div>
            </div>
            
            {% if form_correccion %}
            <div class="card">
                <div class="card-header bg-warning">Corrección Leve</div>
                <div class="card-body">
                    <form method="post" action="{% url 'revisiones:correccion' version.pk %}" enctype="multipart/form-data">
                        {% csrf_token %}
                        {{ form_correccion.detalle }}
                        <div class="mt-2">{{ form_correccion.archivo_corregido }}</div>
                        <button type="submit" class="btn btn-warning w-100 mt-2">
                            Aplicar Corrección
                        </button>
                    </form>
                </div>
            </div>
            {% endif %}
            {% else %}
            <div class="alert alert-info">
                {% if mi_visto %}
                Ya registraste tu visto bueno.
                {% else %}
                Esta versión no está disponible para revisión.
                {% endif %}
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

---

## Tests

```python
# apps/revisiones/tests/test_services.py
import pytest
from django.contrib.auth import get_user_model
from apps.planificaciones.models import Planificacion, Version
from apps.revisiones.services import RevisionService
from apps.revisiones.models import VistoBueno

User = get_user_model()


@pytest.mark.django_db
class TestRevisionService:
    @pytest.fixture
    def setup(self, django_user_model):
        # Crear usuarios
        moderadora = django_user_model.objects.create_user(
            email='mod@ices.edu', password='test', rol='moderadora'
        )
        coordinador = django_user_model.objects.create_user(
            email='coord@ices.edu', password='test', rol='coordinador'
        )
        # ... crear planificación con versión en estado EN_REVISION
        return moderadora, coordinador, version

    def test_doble_aprobacion(self, setup):
        moderadora, coordinador, version = setup
        
        # Primera aprobación
        RevisionService.aprobar(version, moderadora)
        version.refresh_from_db()
        assert version.estado == 'en_revision'  # Aún no oficial
        
        # Segunda aprobación
        RevisionService.aprobar(version, coordinador)
        version.refresh_from_db()
        assert version.estado == 'oficial'  # ¡Ahora sí!
        
        # Verificar vistos
        assert VistoBueno.objects.filter(version=version).count() == 2

    def test_rechazo_requiere_observaciones(self, setup):
        _, _, version = setup
        moderadora = setup[0]
        
        with pytest.raises(ValueError):
            RevisionService.rechazar(version, moderadora, '')
```

---

## Verificación

```bash
# Migraciones
python manage.py makemigrations revisiones
python manage.py migrate

# Tests
pytest apps/revisiones/tests/ -v

# Flujo completo:
# 1. Profesor envía planificación (Fase 4)
# 2. Loguearse como moderadora
# 3. Ver tablero → la planificación aparece
# 4. Revisar → Dar visto bueno
# 5. Loguearse como coordinador de esa carrera
# 6. Revisar → Dar visto bueno → Debe quedar OFICIAL
# 7. Verificar que el profesor ve su planificación como aprobada
```

✅ **Fase 5 completa cuando**: Una planificación puede pasar por el flujo completo: Enviada → En Revisión → Doble Visto → Oficial.

---

## MVP Completado 🎉

Con las fases 0-5 tienes un sistema funcional donde:
- ✅ Moderadora crea instancias
- ✅ Profesor ve sus instancias asignadas
- ✅ Profesor sube Word y lo envía
- ✅ Sistema valida campos obligatorios
- ✅ Moderadora y coordinador revisan
- ✅ Doble aprobación → Oficial

---

## Siguientes pasos (Fases 6-9)

1. **Fase 6**: Consulta pública (Carrera → Año → Materia)
2. **Fase 7**: Notificaciones por email
3. **Fase 8**: Reportes de cumplimiento
4. **Fase 9**: UX, permisos granulares, auditoría

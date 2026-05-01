# Fase 4 — Planificaciones (Profesor)

> Duración estimada: 6-8 horas (la más compleja del MVP)

## Objetivo

El profesor puede subir un documento Word, el sistema lo valida, y se envía al circuito de revisión con versionado.

---

## Checklist

- [ ] Modelo `Planificacion` (agrupa versiones por materia/instancia)
- [ ] Modelo `Version` con FSM de estados
- [ ] Upload de archivos Word
- [ ] Validador de campos obligatorios (python-docx)
- [ ] Versionado automático
- [ ] Marca de entrega tardía
- [ ] Vistas para el profesor
- [ ] Tests

---

## Modelos

```python
# apps/planificaciones/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django_fsm import FSMField, transition


def version_path(instance, filename):
    """media/planificaciones/2026/carrera_1/materia_5/prof_3_v1.docx"""
    p = instance.planificacion
    return (
        f"planificaciones/{p.instancia.anio_academico}/"
        f"carrera_{p.materia.carrera_id}/"
        f"materia_{p.materia_id}/"
        f"prof_{p.profesor_id}_v{instance.numero}_{timezone.now().strftime('%Y%m%d%H%M%S')}.docx"
    )


class Planificacion(models.Model):
    """
    Agrupa todas las versiones de una planificación para una materia/instancia.
    """
    materia = models.ForeignKey(
        'catalogos.Materia',
        on_delete=models.PROTECT,
        related_name='planificaciones'
    )
    profesor = models.ForeignKey(
        'catalogos.Profesor',
        on_delete=models.PROTECT,
        related_name='planificaciones'
    )
    instancia = models.ForeignKey(
        'instancias.InstanciaPresentacion',
        on_delete=models.PROTECT,
        related_name='planificaciones'
    )
    
    # Referencia a la versión oficial vigente (si existe)
    version_oficial = models.OneToOneField(
        'Version',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='es_oficial_de'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('materia', 'profesor', 'instancia')

    def __str__(self):
        return f"{self.materia.nombre} - {self.profesor} ({self.instancia})"

    @property
    def ultima_version(self):
        return self.versiones.order_by('-numero').first()

    @property
    def tiene_oficial(self):
        return self.version_oficial is not None

    def siguiente_numero_version(self):
        ultima = self.versiones.aggregate(models.Max('numero'))['numero__max']
        return (ultima or 0) + 1


class Version(models.Model):
    """
    Una versión específica de una planificación.
    Usa django-fsm para controlar transiciones de estado.
    """
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        ENVIADA = 'enviada', 'Enviada'
        EN_REVISION = 'en_revision', 'En Revisión'
        RECHAZADA_AUTO = 'rechazada_auto', 'Rechazada (Automático)'
        RECHAZADA = 'rechazada', 'Rechazada'
        APROBADA = 'aprobada', 'Aprobada'
        OFICIAL = 'oficial', 'Oficial Vigente'
        REEMPLAZADA = 'reemplazada', 'Reemplazada'

    planificacion = models.ForeignKey(
        Planificacion,
        on_delete=models.CASCADE,
        related_name='versiones'
    )
    numero = models.PositiveSmallIntegerField()
    archivo = models.FileField(upload_to=version_path)
    
    estado = FSMField(
        default=Estado.BORRADOR,
        choices=Estado.choices
    )
    
    # Marca de entrega tardía
    entrega_tardia = models.BooleanField(default=False)
    dias_atraso = models.PositiveSmallIntegerField(default=0)
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    # Observaciones de rechazo automático
    campos_faltantes = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de campos obligatorios faltantes'
    )

    class Meta:
        ordering = ['-numero']
        unique_together = ('planificacion', 'numero')

    def __str__(self):
        return f"v{self.numero} - {self.planificacion.materia.nombre}"

    # === Transiciones FSM ===

    @transition(field=estado, source=Estado.BORRADOR, target=Estado.RECHAZADA_AUTO)
    def rechazar_automaticamente(self, campos_faltantes):
        """Rechazo por falta de campos obligatorios"""
        self.campos_faltantes = campos_faltantes

    @transition(field=estado, source=Estado.BORRADOR, target=Estado.ENVIADA)
    def enviar(self):
        """Envío exitoso tras validación"""
        self.fecha_envio = timezone.now()
        self._calcular_tardia()

    @transition(field=estado, source=Estado.ENVIADA, target=Estado.EN_REVISION)
    def tomar_revision(self):
        """Un revisor toma la planificación para revisar"""
        pass

    @transition(field=estado, source=Estado.EN_REVISION, target=Estado.RECHAZADA)
    def rechazar(self):
        """Rechazo por revisor con observaciones"""
        pass

    @transition(field=estado, source=Estado.EN_REVISION, target=Estado.APROBADA)
    def aprobar(self):
        """Doble visto completado"""
        self.fecha_aprobacion = timezone.now()

    @transition(field=estado, source=Estado.APROBADA, target=Estado.OFICIAL)
    def marcar_oficial(self):
        """Marcar como versión oficial vigente"""
        # Marcar la anterior como reemplazada si existe
        planif = self.planificacion
        if planif.version_oficial and planif.version_oficial != self:
            planif.version_oficial.reemplazar()
            planif.version_oficial.save()
        planif.version_oficial = self
        planif.save()

    @transition(field=estado, source=Estado.OFICIAL, target=Estado.REEMPLAZADA)
    def reemplazar(self):
        """Esta versión fue reemplazada por una nueva oficial"""
        pass

    def _calcular_tardia(self):
        """Calcula si la entrega es tardía"""
        fecha_limite = self.planificacion.instancia.fecha_limite
        hoy = timezone.now().date()
        if hoy > fecha_limite:
            self.entrega_tardia = True
            self.dias_atraso = (hoy - fecha_limite).days
        else:
            self.entrega_tardia = False
            self.dias_atraso = 0
```

---

## Validador de Campos Word

```python
# apps/planificaciones/validators.py
from docx import Document
import re


# Los 7 campos obligatorios (buscar como headings o bold text)
CAMPOS_OBLIGATORIOS = [
    ('proposito', ['propósito', 'proposito', 'objetivo general']),
    ('fundamentacion', ['fundamentación', 'fundamentacion']),
    ('contenidos_minimos', ['contenidos mínimos', 'contenidos minimos']),
    ('metodologia', ['metodología', 'metodologia', 'estrategia']),
    ('requisitos', ['requisitos', 'regularizar', 'promoción', 'promocion']),
    ('evaluacion', ['evaluación', 'evaluacion', 'criterios']),
    ('bibliografia', ['bibliografía', 'bibliografia']),
]


def validar_documento_word(archivo):
    """
    Valida que el documento Word contenga los 7 campos obligatorios.
    Retorna (es_valido, campos_faltantes)
    """
    try:
        doc = Document(archivo)
    except Exception as e:
        return False, ['Error al leer el documento: ' + str(e)]

    # Extraer todo el texto del documento
    texto_completo = []
    
    # Texto de párrafos
    for para in doc.paragraphs:
        texto_completo.append(para.text.lower())
    
    # Texto de tablas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                texto_completo.append(cell.text.lower())
    
    texto = ' '.join(texto_completo)
    
    # Buscar cada campo obligatorio
    campos_faltantes = []
    
    for campo_id, variantes in CAMPOS_OBLIGATORIOS:
        encontrado = False
        for variante in variantes:
            if variante.lower() in texto:
                encontrado = True
                break
        
        if not encontrado:
            campos_faltantes.append(campo_id)
    
    return len(campos_faltantes) == 0, campos_faltantes


def nombre_campo(campo_id):
    """Retorna nombre amigable del campo"""
    nombres = {
        'proposito': 'Propósito',
        'fundamentacion': 'Fundamentación',
        'contenidos_minimos': 'Contenidos Mínimos',
        'metodologia': 'Metodología',
        'requisitos': 'Requisitos para regularizar y promocionar',
        'evaluacion': 'Criterios y formatos de evaluación',
        'bibliografia': 'Bibliografía',
    }
    return nombres.get(campo_id, campo_id)
```

---

## Views

```python
# apps/planificaciones/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from apps.usuarios.decorators import solo_profesor
from apps.catalogos.models import Materia, Plantilla
from apps.instancias.models import InstanciaPresentacion
from .models import Planificacion, Version
from .validators import validar_documento_word, nombre_campo
from .forms import SubirPlanificacionForm


@login_required
@solo_profesor
def cargar_planificacion(request, instancia_id, materia_id):
    """CU-07: Cargar planificación"""
    instancia = get_object_or_404(InstanciaPresentacion, pk=instancia_id)
    materia = get_object_or_404(Materia, pk=materia_id)
    profesor = request.user.perfil_profesor
    
    # Verificar que el profesor es titular de la materia
    if materia.profesor_titular != profesor:
        messages.error(request, 'No eres el titular de esta materia.')
        return redirect('instancias:mis_instancias')
    
    # Obtener o crear la planificación
    planificacion, created = Planificacion.objects.get_or_create(
        materia=materia,
        profesor=profesor,
        instancia=instancia
    )
    
    # Obtener plantilla de la institución del profesor
    plantilla = Plantilla.vigente(profesor.institucion)
    
    if request.method == 'POST':
        form = SubirPlanificacionForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            
            # Crear versión borrador
            version = Version(
                planificacion=planificacion,
                numero=planificacion.siguiente_numero_version(),
                archivo=archivo
            )
            version.save()
            
            messages.success(request, f'Borrador v{version.numero} guardado correctamente.')
            return redirect('planificaciones:detalle', pk=planificacion.pk)
    else:
        form = SubirPlanificacionForm()
    
    context = {
        'instancia': instancia,
        'materia': materia,
        'planificacion': planificacion,
        'plantilla': plantilla,
        'form': form,
        'versiones': planificacion.versiones.all() if not created else [],
    }
    return render(request, 'planificaciones/cargar.html', context)


@login_required
@solo_profesor
def enviar_planificacion(request, version_id):
    """CU-08: Enviar planificación al circuito de revisión"""
    version = get_object_or_404(Version, pk=version_id)
    profesor = request.user.perfil_profesor
    
    # Verificar permisos
    if version.planificacion.profesor != profesor:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('instancias:mis_instancias')
    
    # Verificar estado
    if version.estado != Version.Estado.BORRADOR:
        messages.error(request, 'Esta versión ya fue enviada.')
        return redirect('planificaciones:detalle', pk=version.planificacion.pk)
    
    # Validar documento
    version.archivo.seek(0)
    es_valido, campos_faltantes = validar_documento_word(version.archivo)
    
    if not es_valido:
        # Rechazo automático
        version.rechazar_automaticamente(campos_faltantes)
        version.save()
        
        nombres_faltantes = [nombre_campo(c) for c in campos_faltantes]
        messages.error(
            request, 
            f'El documento no cumple con los campos obligatorios. '
            f'Faltan: {", ".join(nombres_faltantes)}'
        )
    else:
        # Envío exitoso
        version.enviar()
        version.save()
        
        if version.entrega_tardia:
            messages.warning(
                request,
                f'Planificación enviada como ENTREGA TARDÍA ({version.dias_atraso} días de atraso).'
            )
        else:
            messages.success(request, 'Planificación enviada correctamente.')
    
    return redirect('planificaciones:detalle', pk=version.planificacion.pk)


@login_required
def detalle_planificacion(request, pk):
    """Vista de detalle de una planificación con su historial"""
    planificacion = get_object_or_404(Planificacion, pk=pk)
    
    # Verificar permisos
    user = request.user
    if user.es_profesor:
        if planificacion.profesor.usuario != user:
            messages.error(request, 'No tienes acceso a esta planificación.')
            return redirect('instancias:mis_instancias')
    
    context = {
        'planificacion': planificacion,
        'versiones': planificacion.versiones.all(),
        'version_actual': planificacion.ultima_version,
    }
    return render(request, 'planificaciones/detalle.html', context)


@login_required
def descargar_version(request, version_id):
    """Descargar archivo Word de una versión"""
    version = get_object_or_404(Version, pk=version_id)
    
    # TODO: Verificar permisos según rol
    
    return FileResponse(
        version.archivo.open('rb'),
        as_attachment=True,
        filename=f"{version.planificacion.materia.nombre}_v{version.numero}.docx"
    )


@login_required
@solo_profesor
def clonar_oficial_previa(request, materia_id, instancia_id):
    """CU-14: Clonar planificación oficial de período anterior"""
    materia = get_object_or_404(Materia, pk=materia_id)
    instancia_destino = get_object_or_404(InstanciaPresentacion, pk=instancia_id)
    profesor = request.user.perfil_profesor
    
    # Buscar planificaciones oficiales anteriores de esta materia
    planif_anteriores = Planificacion.objects.filter(
        materia=materia,
        version_oficial__isnull=False
    ).exclude(
        instancia=instancia_destino
    ).order_by('-instancia__anio_academico')
    
    if request.method == 'POST':
        version_id = request.POST.get('version_id')
        version_origen = get_object_or_404(Version, pk=version_id)
        
        # Crear nueva planificación y versión borrador
        planif_destino, _ = Planificacion.objects.get_or_create(
            materia=materia,
            profesor=profesor,
            instancia=instancia_destino
        )
        
        # Copiar archivo
        from django.core.files.base import ContentFile
        version_origen.archivo.seek(0)
        contenido = version_origen.archivo.read()
        
        nueva_version = Version(
            planificacion=planif_destino,
            numero=planif_destino.siguiente_numero_version(),
        )
        nueva_version.archivo.save(
            f"clon_v{version_origen.numero}.docx",
            ContentFile(contenido)
        )
        nueva_version.save()
        
        messages.success(request, f'Planificación clonada como borrador v{nueva_version.numero}')
        return redirect('planificaciones:detalle', pk=planif_destino.pk)
    
    context = {
        'materia': materia,
        'instancia_destino': instancia_destino,
        'planificaciones_anteriores': planif_anteriores,
    }
    return render(request, 'planificaciones/clonar.html', context)
```

---

## Forms

```python
# apps/planificaciones/forms.py
from django import forms


class SubirPlanificacionForm(forms.Form):
    archivo = forms.FileField(
        label='Documento Word',
        help_text='Sube tu planificación en formato .doc o .docx'
    )

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        
        # Validar extensión
        nombre = archivo.name.lower()
        if not (nombre.endswith('.doc') or nombre.endswith('.docx')):
            raise forms.ValidationError('Solo se permiten archivos Word (.doc, .docx)')
        
        # Validar tamaño (max 10MB)
        if archivo.size > 10 * 1024 * 1024:
            raise forms.ValidationError('El archivo no puede superar 10MB')
        
        return archivo
```

---

## URLs

```python
# apps/planificaciones/urls.py
from django.urls import path
from . import views

app_name = 'planificaciones'

urlpatterns = [
    path(
        'cargar/<int:instancia_id>/<int:materia_id>/',
        views.cargar_planificacion,
        name='cargar'
    ),
    path(
        'enviar/<int:version_id>/',
        views.enviar_planificacion,
        name='enviar'
    ),
    path('<int:pk>/', views.detalle_planificacion, name='detalle'),
    path('descargar/<int:version_id>/', views.descargar_version, name='descargar'),
    path(
        'clonar/<int:materia_id>/<int:instancia_id>/',
        views.clonar_oficial_previa,
        name='clonar'
    ),
]
```

---

## Template Principal

```html
<!-- templates/planificaciones/detalle.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="{% url 'instancias:mis_instancias' %}">Mis Instancias</a></li>
            <li class="breadcrumb-item">{{ planificacion.instancia.nombre }}</li>
            <li class="breadcrumb-item active">{{ planificacion.materia.nombre }}</li>
        </ol>
    </nav>

    <h2>{{ planificacion.materia.nombre }}</h2>
    <p class="text-muted">
        {{ planificacion.materia.carrera.nombre }} - {{ planificacion.materia.anio_cursado }}° año
        | {{ planificacion.instancia.get_periodo_display }} {{ planificacion.instancia.anio_academico }}
    </p>

    {% if planificacion.tiene_oficial %}
    <div class="alert alert-success">
        <strong>Versión Oficial:</strong> v{{ planificacion.version_oficial.numero }}
        (aprobada el {{ planificacion.version_oficial.fecha_aprobacion|date:"d/m/Y" }})
    </div>
    {% endif %}

    <h4 class="mt-4">Historial de Versiones</h4>
    <table class="table">
        <thead>
            <tr>
                <th>Versión</th>
                <th>Estado</th>
                <th>Fecha Envío</th>
                <th>Tardía</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for v in versiones %}
            <tr class="{% if v.estado == 'oficial' %}table-success{% elif v.estado == 'rechazada' or v.estado == 'rechazada_auto' %}table-danger{% endif %}">
                <td>v{{ v.numero }}</td>
                <td>
                    <span class="badge bg-{{ v.estado|estado_badge }}">
                        {{ v.get_estado_display }}
                    </span>
                </td>
                <td>{{ v.fecha_envio|date:"d/m/Y H:i"|default:"-" }}</td>
                <td>
                    {% if v.entrega_tardia %}
                    <span class="text-danger">Sí ({{ v.dias_atraso }} días)</span>
                    {% else %}
                    -
                    {% endif %}
                </td>
                <td>
                    <a href="{% url 'planificaciones:descargar' v.pk %}" class="btn btn-sm btn-outline-primary">
                        Descargar
                    </a>
                    {% if v.estado == 'borrador' %}
                    <a href="{% url 'planificaciones:enviar' v.pk %}" class="btn btn-sm btn-primary">
                        Enviar
                    </a>
                    {% endif %}
                </td>
            </tr>
            {% if v.estado == 'rechazada_auto' %}
            <tr class="table-warning">
                <td colspan="5">
                    <small>
                        <strong>Campos faltantes:</strong>
                        {% for campo in v.campos_faltantes %}
                        {{ campo|nombre_campo }}{% if not forloop.last %}, {% endif %}
                        {% endfor %}
                    </small>
                </td>
            </tr>
            {% endif %}
            {% empty %}
            <tr>
                <td colspan="5">No hay versiones aún.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% if planificacion.instancia.acepta_envios %}
    <a href="{% url 'planificaciones:cargar' planificacion.instancia.pk planificacion.materia.pk %}" 
       class="btn btn-primary">
        Subir Nueva Versión
    </a>
    {% endif %}
</div>
{% endblock %}
```

---

## Tests

```python
# apps/planificaciones/tests/test_validators.py
import pytest
from io import BytesIO
from docx import Document
from apps.planificaciones.validators import validar_documento_word


def crear_doc_con_campos(campos):
    """Helper para crear un documento Word con ciertos campos"""
    doc = Document()
    for campo in campos:
        doc.add_heading(campo, level=1)
        doc.add_paragraph(f'Contenido de {campo}')
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


class TestValidador:
    def test_documento_completo(self):
        campos = [
            'Propósito', 'Fundamentación', 'Contenidos Mínimos',
            'Metodología', 'Requisitos para regularizar',
            'Criterios de evaluación', 'Bibliografía'
        ]
        doc = crear_doc_con_campos(campos)
        es_valido, faltantes = validar_documento_word(doc)
        assert es_valido
        assert faltantes == []

    def test_documento_incompleto(self):
        campos = ['Propósito', 'Bibliografía']  # Faltan 5
        doc = crear_doc_con_campos(campos)
        es_valido, faltantes = validar_documento_word(doc)
        assert not es_valido
        assert len(faltantes) == 5
```

---

## Verificación

```bash
# Instalar python-docx
pip install python-docx

# Migraciones
python manage.py makemigrations planificaciones
python manage.py migrate

# Tests
pytest apps/planificaciones/tests/ -v

# Flujo completo:
# 1. Crear instancia con carrera/materia
# 2. Loguearse como profesor de esa materia
# 3. Ver la instancia en "Mis Instancias"
# 4. Subir un Word
# 5. Enviar → debe validar campos
# 6. Ver el estado en el historial
```

✅ **Fase 4 completa cuando**: Un profesor puede subir un Word, se validan los campos, y queda con estado "Enviada" o "Rechazada automáticamente".

---

## Siguiente: [Fase 5 - Revisiones](fase-5-revisiones.md)

"""
Vistas ABM para catálogos: Carrera, Profesor, Materia.
Accesibles solo para moderadora y admin.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.usuarios.decorators import gestores
from apps.catalogos.models import Carrera, Profesor, Materia, Institucion
from apps.catalogos.forms import CarreraForm, ProfesorForm, MateriaForm, InstitucionForm

# ─────────────────────── Hub ────────────────────────────────────

@login_required
@gestores
def catalogo_home(request):
    return render(request, 'catalogos/catalogo.html')

# ─────────────────────── Instituciones ─────────────────────────

@login_required
@gestores
def institucion_lista(request):
    instituciones = Institucion.objects.order_by('nombre')
    return render(request, 'catalogos/institucion_lista.html', {'instituciones': instituciones})


@login_required
@gestores
def institucion_crear(request):
    form = InstitucionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Institución creada correctamente.')
        return redirect('catalogos:institucion_lista')
    return render(request, 'catalogos/institucion_form.html',
                  {'form': form, 'titulo': 'Nueva Institución'})


@login_required
@gestores
def institucion_editar(request, pk):
    institucion = get_object_or_404(Institucion, pk=pk)
    form = InstitucionForm(request.POST or None, instance=institucion)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Institución actualizada correctamente.')
        return redirect('catalogos:institucion_lista')
    return render(request, 'catalogos/institucion_form.html',
                  {'form': form, 'titulo': 'Editar Institución', 'objeto': institucion})


@login_required
@gestores
def institucion_eliminar(request, pk):
    institucion = get_object_or_404(Institucion, pk=pk)
    if request.method == 'POST':
        try:
            institucion.delete()
            messages.success(request, 'Institución eliminada.')
        except Exception:
            messages.error(request, 'No se puede eliminar: la institución tiene carreras asociadas.')
        return redirect('catalogos:institucion_lista')
    return render(request, 'catalogos/confirmar_eliminar.html',
                  {'objeto': institucion, 'tipo': 'institución', 'volver': 'catalogos:institucion_lista'})


# ─────────────────────── Carreras ───────────────────────────────

@login_required
@gestores
def carrera_lista(request):
    carreras = Carrera.objects.select_related('institucion', 'coordinador').order_by('institucion', 'nombre')
    return render(request, 'catalogos/carrera_lista.html', {'carreras': carreras})


@login_required
@gestores
def carrera_crear(request):
    form = CarreraForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Carrera creada correctamente.')
        return redirect('catalogos:carrera_lista')
    return render(request, 'catalogos/carrera_form.html', {'form': form, 'titulo': 'Nueva Carrera'})


@login_required
@gestores
def carrera_editar(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    form = CarreraForm(request.POST or None, instance=carrera)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Carrera actualizada correctamente.')
        return redirect('catalogos:carrera_lista')
    return render(request, 'catalogos/carrera_form.html',
                  {'form': form, 'titulo': 'Editar Carrera', 'objeto': carrera})


@login_required
@gestores
def carrera_eliminar(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    if request.method == 'POST':
        try:
            carrera.delete()
            messages.success(request, 'Carrera eliminada.')
        except Exception:
            messages.error(request, 'No se puede eliminar: la carrera tiene materias asociadas.')
        return redirect('catalogos:carrera_lista')
    return render(request, 'catalogos/confirmar_eliminar.html',
                  {'objeto': carrera, 'tipo': 'carrera', 'volver': 'catalogos:carrera_lista'})


# ─────────────────────── Profesores ─────────────────────────────

@login_required
@gestores
def profesor_lista(request):
    profesores = Profesor.objects.select_related('usuario', 'institucion').order_by('usuario__nombre_completo')
    return render(request, 'catalogos/profesor_lista.html', {'profesores': profesores})


@login_required
@gestores
def profesor_crear(request):
    form = ProfesorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profesor creado correctamente.')
        return redirect('catalogos:profesor_lista')
    return render(request, 'catalogos/profesor_form.html', {'form': form, 'titulo': 'Nuevo Profesor'})


@login_required
@gestores
def profesor_editar(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    form = ProfesorForm(request.POST or None, instance=profesor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profesor actualizado correctamente.')
        return redirect('catalogos:profesor_lista')
    return render(request, 'catalogos/profesor_form.html',
                  {'form': form, 'titulo': 'Editar Profesor', 'objeto': profesor})


@login_required
@gestores
def profesor_eliminar(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    if request.method == 'POST':
        try:
            usuario = profesor.usuario
            profesor.delete()
            usuario.delete()
            messages.success(request, 'Profesor eliminado.')
        except Exception:
            messages.error(request, 'No se puede eliminar: el profesor tiene planificaciones asociadas.')
        return redirect('catalogos:profesor_lista')
    return render(request, 'catalogos/confirmar_eliminar.html',
                  {'objeto': profesor, 'tipo': 'profesor', 'volver': 'catalogos:profesor_lista'})


# ─────────────────────── Materias ───────────────────────────────

@login_required
@gestores
def materia_lista(request):
    materias = Materia.objects.select_related(
        'carrera__institucion', 'profesor_titular__usuario'
    ).order_by('carrera', 'anio_cursado', 'nombre')
    return render(request, 'catalogos/materia_lista.html', {'materias': materias})


@login_required
@gestores
def materia_crear(request):
    form = MateriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Materia creada correctamente.')
        return redirect('catalogos:materia_lista')
    return render(request, 'catalogos/materia_form.html', {'form': form, 'titulo': 'Nueva Materia'})


@login_required
@gestores
def materia_editar(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    form = MateriaForm(request.POST or None, instance=materia)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Materia actualizada correctamente.')
        return redirect('catalogos:materia_lista')
    return render(request, 'catalogos/materia_form.html',
                  {'form': form, 'titulo': 'Editar Materia', 'objeto': materia})


@login_required
@gestores
def materia_eliminar(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    if request.method == 'POST':
        try:
            materia.delete()
            messages.success(request, 'Materia eliminada.')
        except Exception:
            messages.error(request, 'No se puede eliminar: la materia tiene planificaciones asociadas.')
        return redirect('catalogos:materia_lista')
    return render(request, 'catalogos/confirmar_eliminar.html',
                  {'objeto': materia, 'tipo': 'materia', 'volver': 'catalogos:materia_lista'})

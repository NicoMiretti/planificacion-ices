# Generated for Catalogos models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import apps.catalogos.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Institucion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('codigo', models.CharField(help_text='Código corto (ICES, UCSE)', max_length=10, unique=True)),
            ],
            options={
                'verbose_name': 'institución',
                'verbose_name_plural': 'instituciones',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='MaterialApoyo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('tipo', models.CharField(choices=[('reglamento', 'Reglamento'), ('calendario', 'Calendario Académico'), ('guia_apa', 'Guía APA'), ('doc_orientador', 'Documento Orientador'), ('otro', 'Otro')], max_length=20)),
                ('nombre', models.CharField(max_length=200)),
                ('archivo', models.FileField(upload_to=apps.catalogos.models.material_path)),
                ('descripcion', models.TextField(blank=True)),
                ('anio_academico', models.PositiveSmallIntegerField(help_text='Año académico al que aplica (ej: 2026)', verbose_name='año académico')),
            ],
            options={
                'verbose_name': 'material de apoyo',
                'verbose_name_plural': 'materiales de apoyo',
                'ordering': ['-anio_academico', 'tipo'],
            },
        ),
        migrations.CreateModel(
            name='Plantilla',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('archivo', models.FileField(help_text='Archivo Word (.doc, .docx)', upload_to=apps.catalogos.models.plantilla_path)),
                ('descripcion', models.CharField(blank=True, max_length=200)),
                ('vigente_desde', models.DateField(help_text='Fecha desde la cual esta plantilla es la oficial', verbose_name='vigente desde')),
                ('institucion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='plantillas', to='catalogos.institucion')),
            ],
            options={
                'verbose_name': 'plantilla',
                'verbose_name_plural': 'plantillas',
                'ordering': ['-vigente_desde'],
            },
        ),
        migrations.CreateModel(
            name='Profesor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('legajo', models.CharField(blank=True, max_length=50)),
                ('institucion', models.ForeignKey(help_text='Institución para notificaciones y plantilla', on_delete=django.db.models.deletion.PROTECT, related_name='profesores', to='catalogos.institucion')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perfil_profesor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'profesor',
                'verbose_name_plural': 'profesores',
                'ordering': ['usuario__nombre_completo', 'usuario__email'],
            },
        ),
        migrations.CreateModel(
            name='Carrera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('nombre', models.CharField(max_length=200)),
                ('coordinador', models.ForeignKey(blank=True, help_text='Coordinador de la carrera (para doble aprobación)', limit_choices_to={'rol': 'coordinador'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carreras_coordinadas', to=settings.AUTH_USER_MODEL)),
                ('institucion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='carreras', to='catalogos.institucion')),
            ],
            options={
                'verbose_name': 'carrera',
                'verbose_name_plural': 'carreras',
                'ordering': ['institucion', 'nombre'],
                'unique_together': {('nombre', 'institucion')},
            },
        ),
        migrations.CreateModel(
            name='Materia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('nombre', models.CharField(max_length=200)),
                ('anio_cursado', models.PositiveSmallIntegerField(help_text='Año de la carrera (1-5)', verbose_name='año de cursado')),
                ('regimen', models.CharField(choices=[('anual', 'Anual'), ('1cuat', '1° Cuatrimestre'), ('2cuat', '2° Cuatrimestre')], default='anual', max_length=10, verbose_name='régimen')),
                ('carrera', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='materias', to='catalogos.carrera')),
                ('profesor_titular', models.ForeignKey(blank=True, help_text='Profesor titular de la materia', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='materias', to='catalogos.profesor')),
            ],
            options={
                'verbose_name': 'materia',
                'verbose_name_plural': 'materias',
                'ordering': ['carrera', 'anio_cursado', 'nombre'],
            },
        ),
    ]

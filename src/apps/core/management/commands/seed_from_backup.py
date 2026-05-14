"""
Management command: seed_from_backup
Carga los datos del archivo dump_data.json (generado por make_backup.py)
en la base de datos local, adaptándose a diferencias de esquema.

Uso:
    python manage.py seed_from_backup
    python manage.py seed_from_backup --json ruta/al/dump_data.json
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction


class Command(BaseCommand):
    help = 'Carga datos desde dump_data.json en la base local'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            default='dump_data.json',
            help='Ruta al archivo dump_data.json (default: dump_data.json en el directorio actual)',
        )
        parser.add_argument(
            '--password',
            default='cambiar123',
            help='Contraseña temporal para todos los usuarios (default: cambiar123)',
        )

    def handle(self, *args, **options):
        json_path = Path(options['json'])
        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f'No se encontró: {json_path}'))
            return

        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        password_hash = make_password(options['password'])

        with transaction.atomic():
            self._seed_instituciones(data)
            self._seed_usuarios(data, password_hash)
            self._seed_carreras(data)
            self._seed_profesores(data)
            self._seed_materias(data)

        self.stdout.write(self.style.SUCCESS('✓ Seed completado exitosamente'))
        self.stdout.write(
            f'  Contraseña temporal para todos los usuarios: {options["password"]}'
        )

    # ─────────────────────────────────────────────────────────────────────────

    def _rows_as_dicts(self, data, table):
        t = data.get(table, {})
        cols = t.get('columns', [])
        rows = t.get('rows', [])
        return [dict(zip(cols, r)) for r in rows]

    def _seed_instituciones(self, data):
        from apps.catalogos.models import Institucion
        rows = self._rows_as_dicts(data, 'catalogos_institucion')
        count = 0
        for r in rows:
            obj, created = Institucion.objects.update_or_create(
                id=r['id'],
                defaults={
                    'nombre': r['nombre'],
                    'codigo': r.get('codigo', r['nombre'][:10].upper()),
                }
            )
            if created:
                count += 1
        self.stdout.write(f'  Instituciones: {len(rows)} procesadas ({count} nuevas)')

    def _seed_usuarios(self, data, password_hash):
        from apps.usuarios.models import Usuario
        rows = self._rows_as_dicts(data, 'usuarios_usuario')
        count = 0
        for r in rows:
            obj, created = Usuario.objects.update_or_create(
                id=r['id'],
                defaults={
                    'email': r['email'],
                    'password': password_hash,
                    'rol': r['rol'],
                    'nombre_completo': r.get('nombre_completo', ''),
                    'is_active': r.get('is_active', True),
                    'is_staff': r.get('is_staff', False),
                    'is_superuser': r.get('is_superuser', False),
                    'first_name': r.get('first_name', ''),
                    'last_name': r.get('last_name', ''),
                }
            )
            if created:
                count += 1
        self.stdout.write(f'  Usuarios: {len(rows)} procesados ({count} nuevos)')

    def _seed_carreras(self, data):
        from apps.catalogos.models import Carrera, Institucion
        from apps.usuarios.models import Usuario
        rows = self._rows_as_dicts(data, 'catalogos_carrera')
        count = 0
        for r in rows:
            coordinador = None
            if r.get('coordinador_id'):
                coordinador = Usuario.objects.filter(id=r['coordinador_id']).first()
            institucion = Institucion.objects.filter(id=r['institucion_id']).first()
            if not institucion:
                self.stderr.write(f'  WARN: institución {r["institucion_id"]} no encontrada para carrera {r["nombre"]}')
                continue
            obj, created = Carrera.objects.update_or_create(
                id=r['id'],
                defaults={
                    'nombre': r['nombre'],
                    'institucion': institucion,
                    'coordinador': coordinador,
                    'activo': r.get('activo', True),
                }
            )
            if created:
                count += 1
        self.stdout.write(f'  Carreras: {len(rows)} procesadas ({count} nuevas)')

    def _seed_profesores(self, data):
        from apps.catalogos.models import Profesor, Institucion
        from apps.usuarios.models import Usuario
        rows = self._rows_as_dicts(data, 'catalogos_profesor')
        count = 0
        for r in rows:
            usuario = Usuario.objects.filter(id=r['usuario_id']).first()
            institucion = Institucion.objects.filter(id=r['institucion_id']).first()
            if not usuario or not institucion:
                self.stderr.write(f'  WARN: usuario o institución no encontrada para profesor id={r["id"]}')
                continue
            obj, created = Profesor.objects.update_or_create(
                id=r['id'],
                defaults={
                    'usuario': usuario,
                    'institucion': institucion,
                    'activo': r.get('activo', True),
                }
            )
            if created:
                count += 1
        self.stdout.write(f'  Profesores: {len(rows)} procesados ({count} nuevos)')

    def _seed_materias(self, data):
        from apps.catalogos.models import Materia, Carrera, Profesor
        rows = self._rows_as_dicts(data, 'catalogos_materia')
        count = 0
        for r in rows:
            carrera = Carrera.objects.filter(id=r['carrera_id']).first()
            if not carrera:
                self.stderr.write(f'  WARN: carrera {r["carrera_id"]} no encontrada para materia {r["nombre"]}')
                continue
            profesor = None
            if r.get('profesor_titular_id'):
                profesor = Profesor.objects.filter(id=r['profesor_titular_id']).first()
            obj, created = Materia.objects.update_or_create(
                id=r['id'],
                defaults={
                    'nombre': r['nombre'],
                    'carrera': carrera,
                    'anio_cursado': r['anio_cursado'],
                    'regimen': r['regimen'],
                    'profesor_titular': profesor,
                    'activo': r.get('activo', True),
                }
            )
            if created:
                count += 1
        self.stdout.write(f'  Materias: {len(rows)} procesadas ({count} nuevas)')

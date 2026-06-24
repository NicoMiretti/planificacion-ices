"""
Script para convertir dump_data.json (formato custom) a Django fixture format.
Genera fixture_seed.json listo para: python manage.py loaddata fixture_seed.json

Ejecutar desde src/: python convertir_dump.py
"""
import json
from datetime import datetime

DEFAULT_TS = '2024-01-01T00:00:00+00:00'

TABLE_MAP = {
    'usuarios_usuario':      'usuarios.usuario',
    'catalogos_institucion': 'catalogos.institucion',
    'catalogos_carrera':     'catalogos.carrera',
    'catalogos_profesor':    'catalogos.profesor',
    'catalogos_materia':     'catalogos.materia',
}

# Columnas que existen en el dump pero NO en el modelo actual → ignorar
SKIP_COLUMNS = {
    'catalogos_carrera': set(),
    'catalogos_materia': set(),
    'catalogos_profesor': set(),
    'catalogos_institucion': set(),
    'usuarios_usuario': set(),
}


def rows_to_dicts(table_data):
    columns = table_data['columns']
    rows = table_data['rows']
    return [dict(zip(columns, row)) for row in rows]


def normalize_col(col):
    """
    Django fixture usa el nombre del campo del modelo, NO el nombre de columna DB.
    Las FK en la DB se llaman campo_id pero en el modelo Django se llaman campo.
    json.load de un dumpdata nativo de Django tampoco incluye el _id.
    """
    if col.endswith('_id'):
        return col[:-3]  # coordinador_id → coordinador
    return col


def convert_table(table_name, rows):
    model_name = TABLE_MAP[table_name]
    skip = SKIP_COLUMNS.get(table_name, set())
    fixtures = []

    for row in rows:
        pk = row['id']
        fields = {}

        for col, val in row.items():
            if col == 'id' or col in skip:
                continue
            field_name = normalize_col(col)
            fields[field_name] = val

        # Solo TimeStampedModel tiene estos campos (no Usuario/AbstractUser)
        if table_name != 'usuarios_usuario':
            if 'fecha_creacion' not in fields:
                fields['fecha_creacion'] = DEFAULT_TS
            if 'fecha_modificacion' not in fields:
                fields['fecha_modificacion'] = DEFAULT_TS
            # modificado_por: null (campo nuevo, FK nullable)
            fields['modificado_por'] = None

        fixtures.append({
            'model': model_name,
            'pk': pk,
            'fields': fields,
        })

    return fixtures


def main():
    with open('dump_data.json', encoding='utf-8') as f:
        data = json.load(f)

    # Orden de carga: usuarios primero (sin FK entre estos), luego catálogos
    order = [
        'usuarios_usuario',
        'catalogos_institucion',
        'catalogos_carrera',
        'catalogos_profesor',
        'catalogos_materia',
    ]

    all_fixtures = []
    for table in order:
        if table not in data:
            print(f'WARN: {table} no encontrada en el dump')
            continue
        rows = rows_to_dicts(data[table])
        fixtures = convert_table(table, rows)
        print(f'{len(fixtures):4d} registros → {TABLE_MAP[table]}')
        all_fixtures.extend(fixtures)

    with open('fixture_seed.json', 'w', encoding='utf-8') as f:
        json.dump(all_fixtures, f, ensure_ascii=False, indent=2, default=str)

    print(f'\nGenerado: fixture_seed.json ({len(all_fixtures)} registros total)')
    print('Cargar con: python manage.py loaddata fixture_seed.json')


if __name__ == '__main__':
    main()

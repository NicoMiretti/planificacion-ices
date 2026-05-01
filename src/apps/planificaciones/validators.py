"""
Validador de documentos Word para planificaciones.
Verifica que el documento contenga los 7 campos obligatorios.
"""
from docx import Document


# Los 7 campos obligatorios con sus variantes de texto aceptadas
CAMPOS_OBLIGATORIOS = [
    ('proposito', ['propósito', 'proposito', 'objetivo general']),
    ('fundamentacion', ['fundamentación', 'fundamentacion']),
    ('contenidos_minimos', ['contenidos mínimos', 'contenidos minimos']),
    ('metodologia', ['metodología', 'metodologia', 'estrategia']),
    ('requisitos', ['requisitos', 'regularizar', 'promoción', 'promocion']),
    ('evaluacion', ['evaluación', 'evaluacion', 'criterios de evaluación', 'criterios de evaluacion']),
    ('bibliografia', ['bibliografía', 'bibliografia']),
]

NOMBRES_CAMPOS = {
    'proposito': 'Propósito',
    'fundamentacion': 'Fundamentación',
    'contenidos_minimos': 'Contenidos Mínimos',
    'metodologia': 'Metodología',
    'requisitos': 'Requisitos para regularizar y promocionar',
    'evaluacion': 'Criterios y formatos de evaluación',
    'bibliografia': 'Bibliografía',
}


def validar_documento_word(archivo):
    """
    Valida que el documento Word contenga los 7 campos obligatorios.

    Args:
        archivo: objeto file-like (FileField abierto o BytesIO)

    Returns:
        (es_valido: bool, campos_faltantes: list[str])
    """
    try:
        doc = Document(archivo)
    except Exception as e:
        return False, [f'error_lectura: {e}']

    # Extraer todo el texto en minúsculas
    textos = []

    for para in doc.paragraphs:
        textos.append(para.text.lower())

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                textos.append(cell.text.lower())

    texto = ' '.join(textos)

    # Buscar cada campo obligatorio
    campos_faltantes = []

    for campo_id, variantes in CAMPOS_OBLIGATORIOS:
        encontrado = any(v.lower() in texto for v in variantes)
        if not encontrado:
            campos_faltantes.append(campo_id)

    return len(campos_faltantes) == 0, campos_faltantes


def nombre_campo(campo_id):
    """Retorna el nombre amigable de un campo por su ID."""
    return NOMBRES_CAMPOS.get(campo_id, campo_id)

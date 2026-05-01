from django import forms


class SubirPlanificacionForm(forms.Form):
    archivo = forms.FileField(
        label='Documento Word',
        help_text='Sube tu planificación en formato .doc o .docx (máx. 10 MB)'
    )

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']

        # Validar extensión
        nombre = archivo.name.lower()
        if not (nombre.endswith('.doc') or nombre.endswith('.docx')):
            raise forms.ValidationError('Solo se permiten archivos Word (.doc, .docx)')

        # Validar tamaño (max 10MB)
        if archivo.size > 10 * 1024 * 1024:
            raise forms.ValidationError('El archivo no puede superar 10 MB')

        return archivo

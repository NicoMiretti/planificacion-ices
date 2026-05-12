from django import forms
from apps.catalogos.models import Carrera, Materia
from .models import InstanciaPresentacion


class InstanciaForm(forms.ModelForm):
    carreras = forms.ModelMultipleChoiceField(
        queryset=Carrera.objects.filter(activo=True).order_by('nombre'),
        widget=forms.CheckboxSelectMultiple,
        label='Carreras',
        help_text='Seleccioná las carreras incluidas en esta instancia.',
    )

    solo_regimen = forms.ChoiceField(
        choices=[
            ('', 'Usar el mismo régimen que el período (recomendado)'),
            ('todos', 'Todas las materias (todos los regímenes)'),
        ] + list(Materia.Regimen.choices),
        required=False,
        label='Filtrar materias por régimen',
        help_text='Por defecto se incluyen solo las materias cuyo régimen coincide con el período elegido.',
    )

    class Meta:
        model = InstanciaPresentacion
        fields = ['nombre', 'anio_academico', 'periodo', 'fecha_apertura', 'fecha_limite', 'solo_regimen', 'carreras']
        widgets = {
            'fecha_apertura': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        labels = {
            'nombre': 'Nombre',
            'anio_academico': 'Año académico',
            'periodo': 'Período',
            'fecha_apertura': 'Fecha de apertura',
            'fecha_limite': 'Fecha límite',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_apertura'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_limite'].input_formats = ['%Y-%m-%d']

    def clean(self):
        cleaned_data = super().clean()
        apertura = cleaned_data.get('fecha_apertura')
        limite = cleaned_data.get('fecha_limite')
        if apertura and limite and limite < apertura:
            raise forms.ValidationError(
                'La fecha límite no puede ser anterior a la fecha de apertura.'
            )

        # Validar que existan materias con titular para la combinación carrera + régimen
        carreras = cleaned_data.get('carreras')
        solo_regimen = cleaned_data.get('solo_regimen')
        periodo = cleaned_data.get('periodo')
        if carreras:
            regimen_efectivo = solo_regimen or periodo
            materias_con_titular = Materia.objects.filter(
                carrera__in=carreras,
                profesor_titular__isnull=False,
                activo=True,
            )
            if regimen_efectivo and regimen_efectivo != 'todos':
                materias_con_titular = materias_con_titular.filter(regimen=regimen_efectivo)
            if not materias_con_titular.exists():
                raise forms.ValidationError(
                    'No hay materias con profesor titular asignado para las carreras y régimen seleccionados. '
                    'Asigná profesores titulares en el catálogo antes de crear la instancia.'
                )

        return cleaned_data

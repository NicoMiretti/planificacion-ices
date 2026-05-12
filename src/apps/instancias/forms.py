from django import forms
from apps.catalogos.models import Carrera
from .models import InstanciaPresentacion


class InstanciaForm(forms.ModelForm):
    carreras = forms.ModelMultipleChoiceField(
        queryset=Carrera.objects.filter(activo=True).order_by('nombre'),
        widget=forms.CheckboxSelectMultiple,
        label='Carreras',
        help_text='Seleccioná las carreras incluidas en esta instancia.',
    )

    class Meta:
        model = InstanciaPresentacion
        fields = ['nombre', 'anio_academico', 'periodo', 'fecha_apertura', 'fecha_limite', 'carreras']
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
        return cleaned_data

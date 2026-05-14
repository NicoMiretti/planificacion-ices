from django import forms
from apps.catalogos.models import Carrera, Materia
from .models import InstanciaPresentacion


class InstanciaForm(forms.ModelForm):
    carreras = forms.ModelMultipleChoiceField(
        queryset=Carrera.objects.filter(activo=True).order_by('nombre'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input carrera-checkbox'}),
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

        # Leer años por carrera desde el POST y validar
        carreras = cleaned_data.get('carreras')
        periodo = cleaned_data.get('periodo')
        anios_cursado = {}  # dict {str(carrera_id): [años]}

        if carreras:
            for carrera in carreras:
                key = f'anios_carrera_{carrera.pk}'
                valores = self.data.getlist(key)
                if not valores:
                    raise forms.ValidationError(
                        f'Seleccioná al menos un año para la carrera "{carrera}".'
                    )
                try:
                    anios_carrera = [int(v) for v in valores]
                except (ValueError, TypeError):
                    raise forms.ValidationError(
                        f'Valores de año inválidos para la carrera "{carrera}".'
                    )
                anios_cursado[str(carrera.pk)] = anios_carrera

                # Validar materias para esta carrera y sus años seleccionados
                materias_carrera = Materia.objects.filter(
                    carrera=carrera,
                    activo=True,
                )
                if periodo and periodo != 'todos':
                    materias_carrera = materias_carrera.filter(regimen=periodo)
                materias_carrera = materias_carrera.filter(anio_cursado__in=anios_carrera)

                materias_sin_profesor = materias_carrera.filter(profesor_titular__isnull=True)
                if materias_sin_profesor.exists():
                    materias_list = ', '.join([m.nombre for m in materias_sin_profesor[:5]])
                    if materias_sin_profesor.count() > 5:
                        materias_list += f', ... (+{materias_sin_profesor.count() - 5} más)'
                    raise forms.ValidationError(
                        f'En "{carrera}" hay materias sin profesor asignado: {materias_list}. '
                        'Asigná un profesor titular antes de crear la instancia.'
                    )

                if not materias_carrera.filter(profesor_titular__isnull=False).exists():
                    raise forms.ValidationError(
                        f'En "{carrera}" no hay materias con profesor titular para los años y régimen seleccionados.'
                    )

        cleaned_data['anios_cursado'] = anios_cursado
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.anios_cursado = self.cleaned_data.get('anios_cursado', {})
        if commit:
            instance.save()
            self.save_m2m()
        return instance

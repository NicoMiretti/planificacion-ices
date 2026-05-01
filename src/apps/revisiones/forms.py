from django import forms


class RechazarForm(forms.Form):
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Indica qué debe corregir el profesor...',
            'class': 'form-control',
        }),
        label='Observaciones',
        required=True
    )


class CorreccionLeveForm(forms.Form):
    detalle = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Describe qué corregiste...',
            'class': 'form-control',
        }),
        label='Detalle de la corrección',
        required=True
    )
    archivo_corregido = forms.FileField(
        label='Documento corregido (opcional)',
        required=False
    )

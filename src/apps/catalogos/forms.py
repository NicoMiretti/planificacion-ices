"""
Formularios para el ABM de catálogos: Institucion, Carrera, Profesor, Materia.
"""
from django import forms
from apps.catalogos.models import Carrera, Profesor, Materia, Institucion


class InstitucionForm(forms.ModelForm):
    class Meta:
        model = Institucion
        fields = ['nombre', 'codigo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'Ej: ICES'}),
        }
        help_texts = {
            'codigo': 'Código corto único (ICES, UCSE, …). No se puede cambiar después si ya tiene carreras.',
        }


class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ['nombre', 'institucion', 'coordinador', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'institucion': forms.Select(attrs={'class': 'form-select'}),
            'coordinador': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.usuarios.models import Usuario
        self.fields['coordinador'].queryset = Usuario.objects.filter(rol='coordinador').order_by('nombre_completo')
        self.fields['coordinador'].empty_label = '— Sin coordinador —'
        self.fields['coordinador'].required = False


class ProfesorForm(forms.ModelForm):
    """Formulario para crear/editar perfil de Profesor (incluye datos del Usuario)."""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    nombre_completo = forms.CharField(
        label='Nombre completo',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label='Contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'autocomplete': 'new-password',
                                          'placeholder': 'Dejar en blanco para no cambiar'}),
        help_text='Solo completar si es un profesor nuevo o si querés cambiar la contraseña.',
    )

    class Meta:
        model = Profesor
        fields = ['institucion']
        widgets = {
            'institucion': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.instance_profesor = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if self.instance_profesor and self.instance_profesor.pk:
            usuario = self.instance_profesor.usuario
            self.fields['email'].initial = usuario.email
            self.fields['nombre_completo'].initial = usuario.nombre_completo

    def clean_email(self):
        from apps.usuarios.models import Usuario
        email = self.cleaned_data['email']
        qs = Usuario.objects.filter(email=email)
        if self.instance_profesor and self.instance_profesor.pk:
            qs = qs.exclude(pk=self.instance_profesor.usuario_id)
        if qs.exists():
            raise forms.ValidationError('Ya existe un usuario con este email.')
        return email

    def clean(self):
        cleaned = super().clean()
        if not self.instance_profesor or not self.instance_profesor.pk:
            if not cleaned.get('password'):
                self.add_error('password', 'La contraseña es obligatoria para un profesor nuevo.')
        return cleaned

    def save(self, commit=True):
        from apps.usuarios.models import Usuario
        profesor = super().save(commit=False)

        email = self.cleaned_data['email']
        nombre = self.cleaned_data['nombre_completo']
        password = self.cleaned_data.get('password')

        if profesor.pk:
            # Edición: actualizar usuario existente
            usuario = profesor.usuario
            usuario.email = email
            usuario.nombre_completo = nombre
            if password:
                usuario.set_password(password)
            if commit:
                usuario.save()
        else:
            # Creación: nuevo usuario con rol=profesor
            usuario = Usuario(email=email, nombre_completo=nombre, rol='profesor')
            usuario.set_password(password)
            if commit:
                usuario.save()
            profesor.usuario = usuario

        if commit:
            profesor.save()
        return profesor


class CoordinadorForm(forms.Form):
    """Formulario para crear/editar un Usuario con rol coordinador."""
    nombre_completo = forms.CharField(
        label='Nombre completo',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label='Contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'autocomplete': 'new-password',
                                          'placeholder': 'Dejar en blanco para no cambiar'}),
        help_text='Solo completar si es un coordinador nuevo o si querés cambiar la contraseña.',
    )

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance  # Usuario existente o None
        initial = kwargs.get('initial', {})
        if instance:
            initial.setdefault('nombre_completo', instance.nombre_completo)
            initial.setdefault('email', instance.email)
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def clean_email(self):
        from apps.usuarios.models import Usuario
        email = self.cleaned_data['email']
        qs = Usuario.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un usuario con este email.')
        return email

    def clean(self):
        cleaned = super().clean()
        if not self.instance:
            if not cleaned.get('password'):
                self.add_error('password', 'La contraseña es obligatoria para un coordinador nuevo.')
        return cleaned

    def save(self):
        from apps.usuarios.models import Usuario
        email = self.cleaned_data['email']
        nombre = self.cleaned_data['nombre_completo']
        password = self.cleaned_data.get('password')
        if self.instance:
            self.instance.email = email
            self.instance.nombre_completo = nombre
            if password:
                self.instance.set_password(password)
            self.instance.save()
            return self.instance
        else:
            usuario = Usuario.objects.create_user(
                email=email,
                nombre_completo=nombre,
                password=password,
                rol='coordinador',
            )
            return usuario


class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['nombre', 'carrera', 'anio_cursado', 'regimen', 'profesor_titular', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'carrera': forms.Select(attrs={'class': 'form-select'}),
            'anio_cursado': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'regimen': forms.Select(attrs={'class': 'form-select'}),
            'profesor_titular': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profesor_titular'].empty_label = '— Sin titular —'
        self.fields['profesor_titular'].required = False

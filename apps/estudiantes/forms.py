"""
============================================================
  MÓDULO: estudiantes — forms.py
============================================================
"""
from django import forms
from .models import Estudiante


class EstudianteForm(forms.ModelForm):
    """
    Formulario principal del estudiante, organizado en secciones
    para uso en vistas web (no admin).
    """

    class Meta:
        model = Estudiante
        exclude = ['created_at', 'updated_at']
        widgets = {
            # Identidad
            'nombres':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres completos'}),
            'apellidos':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos completos'}),
            'cedula':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10 dígitos'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genero':           forms.Select(attrs={'class': 'form-select'}),
            'nacionalidad':     forms.TextInput(attrs={'class': 'form-control'}),
            'etnia':            forms.Select(attrs={'class': 'form-select'}),
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'foto':             forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),

            # Dirección
            'direccion':            forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ciudad':               forms.TextInput(attrs={'class': 'form-control'}),
            'sector':               forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_emergencia':  forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_emergencia':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09XXXXXXXX'}),

            # Médicos
            'tipo_sangre':           forms.Select(attrs={'class': 'form-select'}),
            'alergias':              forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'enfermedades_cronicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medicacion_actual':     forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medico_tratante':       forms.TextInput(attrs={'class': 'form-control'}),
            'seguro_medico':         forms.TextInput(attrs={'class': 'form-control'}),

            # Discapacidad
            'tiene_discapacidad':      forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_tiene_discapacidad'}),
            'tipo_discapacidad':       forms.TextInput(attrs={'class': 'form-control'}),
            'porcentaje_discapacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'numero_conadis':          forms.TextInput(attrs={'class': 'form-control'}),
            'necesidades_especiales':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            # Representante
            'representante':           forms.Select(attrs={'class': 'form-select'}),
            'relacion_representante':  forms.TextInput(attrs={'class': 'form-control'}),

            # Padre
            'padre_nombres':      forms.TextInput(attrs={'class': 'form-control'}),
            'padre_cedula':       forms.TextInput(attrs={'class': 'form-control'}),
            'padre_ocupacion':    forms.TextInput(attrs={'class': 'form-control'}),
            'padre_telefono':     forms.TextInput(attrs={'class': 'form-control'}),
            'padre_email':        forms.EmailInput(attrs={'class': 'form-control'}),
            'padre_estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'padre_instruccion':  forms.Select(attrs={'class': 'form-select'}),

            # Madre
            'madre_nombres':      forms.TextInput(attrs={'class': 'form-control'}),
            'madre_cedula':       forms.TextInput(attrs={'class': 'form-control'}),
            'madre_ocupacion':    forms.TextInput(attrs={'class': 'form-control'}),
            'madre_telefono':     forms.TextInput(attrs={'class': 'form-control'}),
            'madre_email':        forms.EmailInput(attrs={'class': 'form-control'}),
            'madre_estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'madre_instruccion':  forms.Select(attrs={'class': 'form-select'}),

            # Procedencia
            'institucion_anterior': forms.TextInput(attrs={'class': 'form-control'}),
            'amie_anterior':        forms.TextInput(attrs={'class': 'form-control'}),
            'grado_anterior':       forms.TextInput(attrs={'class': 'form-control'}),
            'anio_anterior':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2023-2024'}),
            'promedio_anterior':    forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'max': 10}),
            'motivo_cambio':        forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            # Observaciones
            'observaciones_generales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula and len(cedula) == 10:
            if not Estudiante._validar_cedula_ecuatoriana(cedula):
                raise forms.ValidationError('La cédula ecuatoriana ingresada no es válida.')
        return cedula

    def clean(self):
        cleaned_data = super().clean()
        tiene_discapacidad = cleaned_data.get('tiene_discapacidad')
        tipo_discapacidad  = cleaned_data.get('tipo_discapacidad')

        if tiene_discapacidad and not tipo_discapacidad:
            self.add_error('tipo_discapacidad',
                           'Debe especificar el tipo de discapacidad.')

        return cleaned_data


class EstudianteBusquedaForm(forms.Form):
    """Formulario de búsqueda/filtro de estudiantes."""
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre, apellido o cédula...',
        })
    )
    genero = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + Estudiante.GENEROS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ciudad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'})
    )
    atencion_especial = forms.BooleanField(
        required=False,
        label='Solo con atención especial',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
"""
============================================================
  MÓDULO: periodos — forms.py
============================================================
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import PeriodoAcademico, Nivel, Paralelo


W = {'class': 'form-control'}
WS = {'class': 'form-select'}
WC = {'class': 'form-check-input'}


# DateInput con format='%Y-%m-%d' para que el navegador muestre el date picker
class DateWidget(forms.DateInput):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].update({'class': 'form-control', 'type': 'date'})
        kwargs['format'] = '%Y-%m-%d'
        super().__init__(*args, **kwargs)


class PeriodoAcademicoForm(forms.ModelForm):

    class Meta:
        model  = PeriodoAcademico
        exclude = ['created_at', 'updated_at']
        widgets = {
            'nombre':                   forms.TextInput(attrs={**W, 'placeholder': 'Ej: 2024-2025 Sierra'}),
            'regimen':                  forms.Select(attrs=WS),
            'fecha_inicio':             DateWidget(),
            'fecha_fin':                DateWidget(),
            'fecha_inicio_matriculas':  DateWidget(),
            'fecha_fin_matriculas':     DateWidget(),
            'permite_matricula_extra':  forms.CheckboxInput(attrs=WC),
            'fecha_inicio_extra':       DateWidget(),
            'fecha_fin_extra':          DateWidget(),
            'es_activo':                forms.CheckboxInput(attrs=WC),
            'observaciones':            forms.Textarea(attrs={**W, 'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        errors  = {}

        fi   = cleaned.get('fecha_inicio')
        ff   = cleaned.get('fecha_fin')
        fim  = cleaned.get('fecha_inicio_matriculas')
        ffm  = cleaned.get('fecha_fin_matriculas')
        extra = cleaned.get('permite_matricula_extra')
        fie  = cleaned.get('fecha_inicio_extra')
        ffe  = cleaned.get('fecha_fin_extra')

        if fi and ff and fi >= ff:
            errors['fecha_fin'] = 'El fin del año lectivo debe ser posterior al inicio.'

        if fim and ffm and fim >= ffm:
            errors['fecha_fin_matriculas'] = 'El fin de matrículas debe ser posterior al inicio.'

        # Nota: el inicio de matrículas SÍ puede ser anterior al inicio de clases
        # (es lo normal: se matricula antes de que empiece el año lectivo)
        if fim and ff and fim > ff:
            errors['fecha_inicio_matriculas'] = (
                'El inicio de matrículas no puede ser posterior al fin del año lectivo.'
            )

        if extra:
            if not fie:
                errors['fecha_inicio_extra'] = 'Indique el inicio de matrículas extraordinarias.'
            if not ffe:
                errors['fecha_fin_extra'] = 'Indique el fin de matrículas extraordinarias.'
            if fie and ffe and fie >= ffe:
                errors['fecha_fin_extra'] = (
                    'El fin de matrículas extraordinarias debe ser posterior al inicio.'
                )

        if errors:
            raise ValidationError(errors)

        return cleaned


class NivelForm(forms.ModelForm):

    class Meta:
        model   = Nivel
        exclude = ['created_at', 'updated_at']
        widgets = {
            'nombre':      forms.TextInput(attrs={**W, 'placeholder': 'Ej: 3ro EGB'}),
            'subnivel':    forms.Select(attrs=WS),
            'orden':       forms.NumberInput(attrs={**W, 'min': 1, 'max': 20}),
            'descripcion': forms.TextInput(attrs=W),
        }


class ParaleloForm(forms.ModelForm):

    class Meta:
        model   = Paralelo
        exclude = ['created_at', 'updated_at']
        widgets = {
            'periodo':      forms.Select(attrs=WS),
            'nivel':        forms.Select(attrs=WS),
            'nombre':       forms.TextInput(attrs={**W, 'placeholder': 'Ej: A, B, C'}),
            'cupo_maximo':  forms.NumberInput(attrs={**W, 'min': 1, 'max': 60}),
            'jornada':      forms.Select(attrs=WS),
            'observaciones':forms.Textarea(attrs={**W, 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar todos los períodos ordenados por más reciente
        self.fields['periodo'].queryset = PeriodoAcademico.objects.order_by('-fecha_inicio')
        # Etiqueta con indicador de activo
        self.fields['periodo'].label_from_instance = lambda p: (
            f"{p.nombre} {'★ activo' if p.es_activo else ''}"
        )

    def clean(self):
        cleaned = super().clean()
        paralelo = Paralelo.objects.filter(
            periodo=cleaned.get('periodo'),
            nivel=cleaned.get('nivel'),
            nombre=cleaned.get('nombre'),
        ).exclude(pk=self.instance.pk if self.instance else None)

        if paralelo.exists():
            raise ValidationError(
                'Ya existe un paralelo con ese nivel e identificador en este período.'
            )
        return cleaned
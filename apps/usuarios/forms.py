"""
============================================================
  MÓDULO: usuarios — forms.py
============================================================
"""
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm, PasswordChangeForm, SetPasswordForm
)
from django.core.exceptions import ValidationError
from .models import Usuario


W  = {'class': 'form-control'}
WS = {'class': 'form-select'}
WC = {'class': 'form-check-input'}
WP = {'class': 'form-control', 'type': 'password'}


class DateWidget(forms.DateInput):
    """DateInput que siempre renderiza type=date con formato ISO."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].update({'class': 'form-control', 'type': 'date'})
        kwargs['format'] = '%Y-%m-%d'
        super().__init__(*args, **kwargs)


# ── Registro de representante (portal público) ────────────────────────────────

class RegistroRepresentanteForm(UserCreationForm):
    """
    Formulario de auto-registro para representantes legales.
    El rol queda fijo como REPRESENTANTE.
    """
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={**WP, 'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={**WP, 'autocomplete': 'new-password'}),
    )

    class Meta:
        model  = Usuario
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'cedula',
            'telefono', 'telefono_alt',
            'direccion', 'ciudad', 'sector',
            'fecha_nacimiento', 'foto',
        ]
        widgets = {
            'username':        forms.TextInput(attrs={**W, 'autocomplete': 'username'}),
            'first_name':      forms.TextInput(attrs={**W, 'placeholder': 'Nombres'}),
            'last_name':       forms.TextInput(attrs={**W, 'placeholder': 'Apellidos'}),
            'email':           forms.EmailInput(attrs={**W, 'placeholder': 'correo@ejemplo.com'}),
            'cedula':          forms.TextInput(attrs={**W, 'placeholder': '10 dígitos'}),
            'telefono':        forms.TextInput(attrs={**W, 'placeholder': '09XXXXXXXX'}),
            'telefono_alt':    forms.TextInput(attrs={**W, 'placeholder': 'Opcional'}),
            'direccion':       forms.Textarea(attrs={**W, 'rows': 2}),
            'ciudad':          forms.TextInput(attrs=W),
            'sector':          forms.TextInput(attrs=W),
            'fecha_nacimiento':DateWidget(),
            'foto':            forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email__iexact=email).exists():
            raise ValidationError('Ya existe una cuenta con este correo electrónico.')
        return email.lower() if email else email

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula and len(cedula) == 10:
            if not _validar_cedula_ec(cedula):
                raise ValidationError('La cédula ecuatoriana ingresada no es válida.')
        return cedula

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol        = Usuario.ROL_REPRESENTANTE
        user.is_active  = True   # Activo pero sin verificar email
        user.is_verified = False
        if commit:
            user.save()
        return user


# ── Formulario de edición de perfil (para el propio usuario) ─────────────────

class PerfilForm(forms.ModelForm):
    """Permite al usuario editar sus propios datos (sin rol ni permisos)."""

    class Meta:
        model  = Usuario
        fields = [
            'first_name', 'last_name', 'email',
            'cedula', 'telefono', 'telefono_alt',
            'fecha_nacimiento', 'direccion', 'ciudad', 'sector', 'foto',
        ]
        widgets = {
            'first_name':      forms.TextInput(attrs=W),
            'last_name':       forms.TextInput(attrs=W),
            'email':           forms.EmailInput(attrs=W),
            'cedula':          forms.TextInput(attrs=W),
            'telefono':        forms.TextInput(attrs=W),
            'telefono_alt':    forms.TextInput(attrs=W),
            'fecha_nacimiento':DateWidget(),
            'direccion':       forms.Textarea(attrs={**W, 'rows': 2}),
            'ciudad':          forms.TextInput(attrs=W),
            'sector':          forms.TextInput(attrs=W),
            'foto':            forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = Usuario.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('Este correo ya está en uso por otro usuario.')
        return email.lower() if email else email

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula and len(cedula) == 10:
            if not _validar_cedula_ec(cedula):
                raise ValidationError('La cédula ecuatoriana ingresada no es válida.')
        return cedula


# ── Formulario de edición de usuario por Admin/Secretaria ────────────────────

class UsuarioAdminForm(forms.ModelForm):
    """Para editar usuarios desde vistas internas del sistema (no el admin de Django)."""

    class Meta:
        model  = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'cedula', 'telefono', 'telefono_alt',
            'rol', 'is_active', 'is_verified',
            'fecha_nacimiento', 'direccion', 'ciudad', 'sector', 'foto',
        ]
        widgets = {
            'username':        forms.TextInput(attrs=W),
            'first_name':      forms.TextInput(attrs=W),
            'last_name':       forms.TextInput(attrs=W),
            'email':           forms.EmailInput(attrs=W),
            'cedula':          forms.TextInput(attrs=W),
            'telefono':        forms.TextInput(attrs=W),
            'telefono_alt':    forms.TextInput(attrs=W),
            'rol':             forms.Select(attrs=WS),
            'is_active':       forms.CheckboxInput(attrs=WC),
            'is_verified':     forms.CheckboxInput(attrs=WC),
            'fecha_nacimiento':DateWidget(),
            'direccion':       forms.Textarea(attrs={**W, 'rows': 2}),
            'ciudad':          forms.TextInput(attrs=W),
            'sector':          forms.TextInput(attrs=W),
            'foto':            forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


# ── Cambio de contraseña con Bootstrap ───────────────────────────────────────

class CambioPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class SetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# ── Login ─────────────────────────────────────────────────────────────────────

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario o correo',
        widget=forms.TextInput(attrs={**W, 'autofocus': True, 'placeholder': 'Usuario o correo'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={**WP, 'placeholder': 'Contraseña'})
    )
    recordarme = forms.BooleanField(
        required=False,
        label='Recordarme',
        widget=forms.CheckboxInput(attrs=WC)
    )


# ── Formulario de creación de usuario por Admin ───────────────────────────────

class UsuarioCreateForm(UserCreationForm):
    """
    Admin crea un usuario con rol, contraseña y datos básicos.
    Basado en UserCreationForm para manejar correctamente el hash de contraseña.
    """
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={**WP, 'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={**WP, 'autocomplete': 'new-password'}),
    )

    class Meta:
        model  = Usuario
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'cedula', 'telefono', 'telefono_alt',
            'fecha_nacimiento', 'direccion', 'ciudad', 'sector',
            'foto', 'rol', 'is_active', 'is_verified',
        ]
        widgets = {
            'username':         forms.TextInput(attrs=W),
            'first_name':       forms.TextInput(attrs=W),
            'last_name':        forms.TextInput(attrs=W),
            'email':            forms.EmailInput(attrs=W),
            'cedula':           forms.TextInput(attrs=W),
            'telefono':         forms.TextInput(attrs=W),
            'telefono_alt':     forms.TextInput(attrs=W),
            'fecha_nacimiento': DateWidget(),
            'direccion':        forms.Textarea(attrs={**W, 'rows': 2}),
            'ciudad':           forms.TextInput(attrs=W),
            'sector':           forms.TextInput(attrs=W),
            'foto':             forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'rol':              forms.Select(attrs=WS),
            'is_active':        forms.CheckboxInput(attrs=WC),
            'is_verified':      forms.CheckboxInput(attrs=WC),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula and len(cedula) == 10:
            if not _validar_cedula_ec(cedula):
                raise ValidationError('La cédula ecuatoriana ingresada no es válida.')
        return cedula


# ── Utilidades ────────────────────────────────────────────────────────────────

def _validar_cedula_ec(cedula: str) -> bool:
    try:
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        total = 0
        for i, c in enumerate(coeficientes):
            v = int(cedula[i]) * c
            total += v - 9 if v > 9 else v
        return (10 - (total % 10)) % 10 == int(cedula[9])
    except (ValueError, IndexError):
        return False
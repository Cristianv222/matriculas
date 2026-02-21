"""
Formularios del mÃ³dulo de usuarios
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesiÃ³n personalizado"""
    username = forms.CharField(
        label='CÃ©dula o Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su cÃ©dula'})
    )
    password = forms.CharField(
        label='ContraseÃ±a',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'ContraseÃ±a'})
    )


class RegistroRepresentanteForm(UserCreationForm):
    """Formulario de registro para representantes legales"""
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'cedula', 'email', 'telefono', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = Usuario.ROL_REPRESENTANTE
        user.username = self.cleaned_data['cedula']
        if commit:
            user.save()
        return user

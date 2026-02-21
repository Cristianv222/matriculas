"""
Vistas del mÃ³dulo de usuarios
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistroRepresentanteForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'Bienvenido, {form.get_user().get_full_name()}')
        return redirect('matriculas:dashboard')
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'SesiÃ³n cerrada correctamente.')
    return redirect('usuarios:login')


def registro_view(request):
    form = RegistroRepresentanteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Cuenta creada exitosamente.')
        return redirect('matriculas:dashboard')
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def perfil_view(request):
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Estudiante


@login_required
def lista_estudiantes(request):
    if request.user.es_secretaria:
        estudiantes = Estudiante.objects.filter(is_active=True)
    else:
        estudiantes = Estudiante.objects.filter(representante=request.user, is_active=True)
    return render(request, 'estudiantes/lista.html', {'estudiantes': estudiantes})


@login_required
def detalle_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    return render(request, 'estudiantes/detalle.html', {'estudiante': estudiante})

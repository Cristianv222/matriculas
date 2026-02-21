from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Matricula


@login_required
def dashboard(request):
    """Panel principal segÃºn el rol del usuario"""
    if request.user.es_secretaria:
        pendientes = Matricula.objects.filter(estado=Matricula.ESTADO_PENDIENTE).count()
        en_revision = Matricula.objects.filter(estado=Matricula.ESTADO_EN_REVISION).count()
        aprobadas = Matricula.objects.filter(estado=Matricula.ESTADO_APROBADA).count()
        context = {
            'pendientes': pendientes,
            'en_revision': en_revision,
            'aprobadas': aprobadas,
            'ultimas_solicitudes': Matricula.objects.filter(estado=Matricula.ESTADO_PENDIENTE)[:10],
        }
    else:
        mis_matriculas = Matricula.objects.filter(solicitante=request.user)
        context = {'mis_matriculas': mis_matriculas}
    return render(request, 'matriculas/dashboard.html', context)


@login_required
def lista_matriculas(request):
    if request.user.es_secretaria:
        matriculas = Matricula.objects.all().select_related('estudiante', 'paralelo', 'solicitante')
    else:
        matriculas = Matricula.objects.filter(solicitante=request.user)

    estado = request.GET.get('estado')
    if estado:
        matriculas = matriculas.filter(estado=estado)

    return render(request, 'matriculas/lista.html', {
        'matriculas': matriculas,
        'estados': Matricula.ESTADOS,
    })


@login_required
def detalle_matricula(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    return render(request, 'matriculas/detalle.html', {'matricula': matricula})

"""
Reportes, estadÃ­sticas y exportaciÃ³n de datos
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.matriculas.models import Matricula
from apps.periodos.models import PeriodoAcademico, Paralelo


@login_required
def dashboard_reportes(request):
    """Panel de reportes y estadÃ­sticas"""
    periodo_activo = PeriodoAcademico.objects.filter(es_activo=True).first()

    stats = {}
    if periodo_activo:
        matriculas = Matricula.objects.filter(paralelo__periodo=periodo_activo)
        stats = {
            'total': matriculas.count(),
            'aprobadas': matriculas.filter(estado=Matricula.ESTADO_APROBADA).count(),
            'pendientes': matriculas.filter(estado=Matricula.ESTADO_PENDIENTE).count(),
            'rechazadas': matriculas.filter(estado=Matricula.ESTADO_RECHAZADA).count(),
        }

    return render(request, 'reportes/dashboard.html', {
        'periodo': periodo_activo,
        'stats': stats,
    })


@login_required
def reporte_matriculados(request):
    """Listado de matriculados por nivel y paralelo"""
    periodo_activo = PeriodoAcademico.objects.filter(es_activo=True).first()
    paralelos = Paralelo.objects.filter(
        periodo=periodo_activo,
        is_active=True
    ).prefetch_related('matriculas__estudiante') if periodo_activo else []

    return render(request, 'reportes/matriculados.html', {
        'periodo': periodo_activo,
        'paralelos': paralelos,
    })

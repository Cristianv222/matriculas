from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PeriodoAcademico, Nivel, Paralelo


@login_required
def lista_paralelos(request):
    periodo_activo = PeriodoAcademico.objects.filter(es_activo=True).first()
    paralelos = Paralelo.objects.filter(periodo=periodo_activo, is_active=True) if periodo_activo else []
    return render(request, 'periodos/paralelos.html', {
        'periodo': periodo_activo,
        'paralelos': paralelos
    })

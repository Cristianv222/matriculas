from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DocumentoMatricula


@login_required
def lista_documentos_matricula(request, matricula_pk):
    from apps.matriculas.models import Matricula
    matricula = get_object_or_404(Matricula, pk=matricula_pk)
    documentos = DocumentoMatricula.objects.filter(matricula=matricula)
    return render(request, 'documentos/lista.html', {
        'matricula': matricula,
        'documentos': documentos
    })

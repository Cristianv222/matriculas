from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notificacion


@login_required
def lista_notificaciones(request):
    notificaciones = Notificacion.objects.filter(destinatario=request.user)
    # Marcar como leÃ­das
    notificaciones.filter(leida=False).update(leida=True)
    return render(request, 'notificaciones/lista.html', {'notificaciones': notificaciones})

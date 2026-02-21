"""
Servicio de notificaciones: email + notificaciones internas
"""
from .models import Notificacion
from apps.core.utils import enviar_email_sistema


def notificar_solicitud_recibida(matricula):
    """Notifica al representante que su solicitud fue recibida"""
    Notificacion.objects.create(
        destinatario=matricula.solicitante,
        tipo=Notificacion.TIPO_INFO,
        titulo='Solicitud de matrÃ­cula recibida',
        mensaje=f'Su solicitud de matrÃ­cula para {matricula.estudiante.nombre_completo} '
                f'ha sido recibida. CÃ³digo: {matricula.codigo}',
        url_accion=f'/matriculas/{matricula.pk}/'
    )
    enviar_email_sistema(
        destinatario=matricula.solicitante.email,
        asunto=f'[SFQ] Solicitud recibida - {matricula.codigo}',
        mensaje=f'Su solicitud de matrÃ­cula ha sido registrada exitosamente.\n'
                f'CÃ³digo: {matricula.codigo}\n'
                f'Estado: Pendiente de revisiÃ³n\n\n'
                f'Le notificaremos cuando haya novedades.'
    )


def notificar_matricula_aprobada(matricula):
    """Notifica al representante que la matrÃ­cula fue aprobada"""
    Notificacion.objects.create(
        destinatario=matricula.solicitante,
        tipo=Notificacion.TIPO_EXITO,
        titulo='Â¡MatrÃ­cula aprobada!',
        mensaje=f'La matrÃ­cula de {matricula.estudiante.nombre_completo} '
                f'ha sido APROBADA. Puede descargar el certificado.',
        url_accion=f'/matriculas/{matricula.pk}/'
    )
    enviar_email_sistema(
        destinatario=matricula.solicitante.email,
        asunto=f'[SFQ] MatrÃ­cula aprobada - {matricula.codigo}',
        mensaje=f'Â¡Felicitaciones! La matrÃ­cula de {matricula.estudiante.nombre_completo} '
                f'ha sido aprobada.\n\nIngrese al sistema para descargar el certificado.'
    )


def notificar_matricula_rechazada(matricula):
    """Notifica al representante que la matrÃ­cula fue rechazada"""
    Notificacion.objects.create(
        destinatario=matricula.solicitante,
        tipo=Notificacion.TIPO_ADVERTENCIA,
        titulo='MatrÃ­cula requiere correcciones',
        mensaje=f'Su solicitud requiere correcciones. Motivo: {matricula.motivo_rechazo}',
        url_accion=f'/matriculas/{matricula.pk}/'
    )

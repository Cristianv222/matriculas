"""
Utilidades compartidas del sistema
"""
import shortuuid
from django.core.mail import send_mail
from django.conf import settings


def generar_codigo_matricula():
    """Genera un cÃ³digo Ãºnico para la matrÃ­cula"""
    return f"MAT-{shortuuid.uuid()[:8].upper()}"


def enviar_email_sistema(destinatario, asunto, mensaje):
    """Wrapper para envÃ­o de emails del sistema"""
    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@sfq.edu.ec',
        recipient_list=[destinatario],
        fail_silently=True,
    )

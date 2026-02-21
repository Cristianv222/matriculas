"""
Notificaciones internas del sistema
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.usuarios.models import Usuario


class Notificacion(TimeStampedModel):
    TIPO_INFO = 'INFO'
    TIPO_EXITO = 'EXITO'
    TIPO_ADVERTENCIA = 'ADVERTENCIA'
    TIPO_ERROR = 'ERROR'

    TIPOS = [
        (TIPO_INFO, 'InformaciÃ³n'),
        (TIPO_EXITO, 'Ã‰xito'),
        (TIPO_ADVERTENCIA, 'Advertencia'),
        (TIPO_ERROR, 'Error'),
    ]

    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=15, choices=TIPOS, default=TIPO_INFO)
    titulo = models.CharField(max_length=200, verbose_name='TÃ­tulo')
    mensaje = models.TextField(verbose_name='Mensaje')
    leida = models.BooleanField(default=False, verbose_name='LeÃ­da')
    url_accion = models.CharField(max_length=200, blank=True, verbose_name='URL de acciÃ³n')

    class Meta:
        verbose_name = 'NotificaciÃ³n'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} â†’ {self.destinatario}"

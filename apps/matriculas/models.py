"""
Modelo principal del proceso de matrÃ­cula
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.usuarios.models import Usuario
from apps.estudiantes.models import Estudiante
from apps.periodos.models import Paralelo


class Matricula(TimeStampedModel):
    """
    Solicitud y proceso completo de matrÃ­cula
    """
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_EN_REVISION = 'EN_REVISION'
    ESTADO_APROBADA = 'APROBADA'
    ESTADO_RECHAZADA = 'RECHAZADA'
    ESTADO_ANULADA = 'ANULADA'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente de revisiÃ³n'),
        (ESTADO_EN_REVISION, 'En revisiÃ³n'),
        (ESTADO_APROBADA, 'Aprobada'),
        (ESTADO_RECHAZADA, 'Rechazada'),
        (ESTADO_ANULADA, 'Anulada'),
    ]

    TIPO_NUEVA = 'NUEVA'
    TIPO_RENOVACION = 'RENOVACION'
    TIPOS = [
        (TIPO_NUEVA, 'Primera matrÃ­cula'),
        (TIPO_RENOVACION, 'RenovaciÃ³n'),
    ]

    # Datos principales
    codigo = models.CharField(max_length=20, unique=True, verbose_name='CÃ³digo de matrÃ­cula')
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='matriculas')
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE, related_name='matriculas')
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='matriculas_solicitadas')
    tipo = models.CharField(max_length=15, choices=TIPOS, default=TIPO_NUEVA)
    estado = models.CharField(max_length=15, choices=ESTADOS, default=ESTADO_PENDIENTE)

    # Seguimiento
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    revisado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matriculas_revisadas'
    )
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    motivo_rechazo = models.TextField(blank=True, verbose_name='Motivo de rechazo')

    class Meta:
        verbose_name = 'MatrÃ­cula'
        verbose_name_plural = 'MatrÃ­culas'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.codigo} - {self.estudiante}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            from apps.core.utils import generar_codigo_matricula
            self.codigo = generar_codigo_matricula()
        super().save(*args, **kwargs)


class HistorialMatricula(models.Model):
    """Registro de cambios de estado en la matrÃ­cula"""
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=15)
    estado_nuevo = models.CharField(max_length=15)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.matricula.codigo}: {self.estado_anterior} â†’ {self.estado_nuevo}"

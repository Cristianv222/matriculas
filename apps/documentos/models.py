"""
GestiÃ³n de documentos requeridos para la matrÃ­cula
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.matriculas.models import Matricula


class TipoDocumento(TimeStampedModel):
    """CatÃ¡logo de tipos de documentos requeridos"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre del documento')
    descripcion = models.TextField(blank=True, verbose_name='DescripciÃ³n/Instrucciones')
    es_obligatorio = models.BooleanField(default=True, verbose_name='Es obligatorio')
    aplica_primera_vez = models.BooleanField(default=True, verbose_name='Aplica para primera matrÃ­cula')
    aplica_renovacion = models.BooleanField(default=False, verbose_name='Aplica para renovaciÃ³n')
    aplica_discapacidad = models.BooleanField(default=False, verbose_name='Aplica para discapacidad')
    formatos_permitidos = models.CharField(max_length=100, default='PDF,JPG,PNG', verbose_name='Formatos permitidos')

    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class DocumentoMatricula(TimeStampedModel):
    """Documento subido para una matrÃ­cula especÃ­fica"""
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_VERIFICADO = 'VERIFICADO'
    ESTADO_RECHAZADO = 'RECHAZADO'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente de verificaciÃ³n'),
        (ESTADO_VERIFICADO, 'Verificado'),
        (ESTADO_RECHAZADO, 'Rechazado'),
    ]

    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='documentos/matriculas/%Y/%m/', verbose_name='Archivo')
    estado = models.CharField(max_length=15, choices=ESTADOS, default=ESTADO_PENDIENTE)
    observacion = models.TextField(blank=True, verbose_name='ObservaciÃ³n del revisor')
    verificado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_verificados'
    )

    class Meta:
        verbose_name = 'Documento de MatrÃ­cula'
        verbose_name_plural = 'Documentos de MatrÃ­cula'

    def __str__(self):
        return f"{self.tipo} - {self.matricula.codigo}"

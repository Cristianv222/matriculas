"""
============================================================
  MÓDULO: documentos
  Catálogo de requisitos y gestión de archivos por matrícula
============================================================
"""
import os
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from apps.core.models import TimeStampedModel
from apps.matriculas.models import Matricula


def validar_tamano_archivo(archivo):
    """Valida que el archivo no supere 10 MB."""
    limite_mb = 10
    if archivo.size > limite_mb * 1024 * 1024:
        raise ValidationError(f'El archivo no puede superar {limite_mb} MB.')


def ruta_documento(instance, filename):
    """Genera la ruta de almacenamiento del documento."""
    ext = filename.split('.')[-1]
    return (f'documentos/matriculas/'
            f'{instance.matricula.paralelo.periodo_id}/'
            f'{instance.matricula.codigo}/'
            f'{instance.tipo.codigo}_{instance.pk}.{ext}')


class TipoDocumento(TimeStampedModel):
    """
    Catálogo de tipos de documentos requeridos para la matrícula.
    El administrador configura aquí qué se pide y cuándo.
    """
    # ─── Datos del catálogo ───────────────────────────────────────────────────
    # ✅ CORREGIDO: se agrega default='' para evitar el prompt interactivo en makemigrations.
    #    Una vez migrado, asigna códigos reales desde el admin y puedes remover el default
    #    si quieres forzar que sea obligatorio en nuevos registros.
    codigo       = models.CharField(max_length=30, unique=True,
                                    default='',
                                    verbose_name='Código interno',
                                    help_text='Ej: CEDULA_ESTUDIANTE, PARTIDA_NACIMIENTO')
    nombre       = models.CharField(max_length=150, verbose_name='Nombre del documento')
    descripcion  = models.TextField(blank=True,
                                    verbose_name='Descripción / Instrucciones al representante',
                                    help_text='Explique cómo debe presentarse el documento.')
    orden        = models.PositiveIntegerField(default=0,
                                               verbose_name='Orden de presentación')

    # ─── Cuándo aplica ────────────────────────────────────────────────────────
    es_obligatorio        = models.BooleanField(default=True,
                                                verbose_name='Es obligatorio')
    aplica_primera_vez    = models.BooleanField(default=True,
                                                verbose_name='Aplica para primera matrícula')
    aplica_renovacion     = models.BooleanField(default=False,
                                                verbose_name='Aplica para renovación')
    aplica_traslado       = models.BooleanField(default=True,
                                                verbose_name='Aplica para traslado')
    aplica_discapacidad   = models.BooleanField(default=False,
                                                verbose_name='Aplica solo si tiene discapacidad')

    # ─── Restricciones del archivo ────────────────────────────────────────────
    formatos_permitidos   = models.CharField(max_length=100, default='pdf,jpg,jpeg,png',
                                             verbose_name='Formatos permitidos',
                                             help_text='Extensiones separadas por coma. Ej: pdf,jpg,png')
    tamano_maximo_mb      = models.PositiveIntegerField(default=10,
                                                        verbose_name='Tamaño máximo (MB)')

    class Meta:
        verbose_name        = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documentos'
        ordering            = ['orden', 'nombre']

    def __str__(self):
        obligatorio = '(*) ' if self.es_obligatorio else ''
        return f'{obligatorio}{self.nombre}'

    def aplica_para_matricula(self, matricula):
        """
        Devuelve True si este tipo de documento aplica para
        el tipo y condiciones de la matrícula dada.
        """
        from apps.matriculas.models import Matricula as M
        tipo = matricula.tipo
        tiene_discapacidad = matricula.estudiante.tiene_discapacidad

        if tipo == M.TIPO_NUEVA and not self.aplica_primera_vez:
            return False
        if tipo == M.TIPO_RENOVACION and not self.aplica_renovacion:
            return False
        if tipo == M.TIPO_TRASLADO_ENTRADA and not self.aplica_traslado:
            return False
        if self.aplica_discapacidad and not tiene_discapacidad:
            return False
        return True

    @property
    def extensiones_lista(self):
        return [ext.strip().lower() for ext in self.formatos_permitidos.split(',')]


class DocumentoMatricula(TimeStampedModel):
    """
    Archivo concreto subido por el representante para una matrícula.
    Cada documento pasa por revisión de la secretaría.
    """
    ESTADO_PENDIENTE   = 'PENDIENTE'
    ESTADO_VERIFICADO  = 'VERIFICADO'
    ESTADO_RECHAZADO   = 'RECHAZADO'

    ESTADOS = [
        (ESTADO_PENDIENTE,  'Pendiente de verificación'),
        (ESTADO_VERIFICADO, 'Verificado y aceptado'),
        (ESTADO_RECHAZADO,  'Rechazado — debe volver a subir'),
    ]

    # ─── Relaciones ───────────────────────────────────────────────────────────
    matricula       = models.ForeignKey(Matricula, on_delete=models.CASCADE,
                                        related_name='documentos',
                                        verbose_name='Matrícula')
    tipo            = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE,
                                        verbose_name='Tipo de documento')

    # ─── Archivo ──────────────────────────────────────────────────────────────
    archivo         = models.FileField(
                          upload_to=ruta_documento,
                          verbose_name='Archivo',
                          validators=[
                              FileExtensionValidator(
                                  allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']
                              ),
                              validar_tamano_archivo,
                          ]
                      )
    nombre_original = models.CharField(max_length=255, blank=True,
                                       verbose_name='Nombre original del archivo')
    tamano_bytes    = models.PositiveIntegerField(blank=True, null=True,
                                                  verbose_name='Tamaño en bytes')

    # ─── Estado de verificación ───────────────────────────────────────────────
    estado          = models.CharField(max_length=15, choices=ESTADOS,
                                       default=ESTADO_PENDIENTE, verbose_name='Estado')
    observacion     = models.TextField(blank=True,
                                       verbose_name='Observación del revisor',
                                       help_text='Visible al representante. Indique por qué se rechazó.')
    verificado_por  = models.ForeignKey(
                          'usuarios.Usuario',
                          on_delete=models.SET_NULL,
                          null=True, blank=True,
                          related_name='documentos_verificados',
                          verbose_name='Verificado por'
                      )
    fecha_verificacion = models.DateTimeField(blank=True, null=True,
                                              verbose_name='Fecha de verificación')

    class Meta:
        verbose_name        = 'Documento de Matrícula'
        verbose_name_plural = 'Documentos de Matrícula'
        ordering            = ['tipo__orden']
        unique_together     = [['matricula', 'tipo']]

    def __str__(self):
        return f'{self.tipo.nombre} — {self.matricula.codigo}'

    def save(self, *args, **kwargs):
        if self.archivo and not self.nombre_original:
            self.nombre_original = os.path.basename(self.archivo.name)
        if self.archivo and not self.tamano_bytes:
            try:
                self.tamano_bytes = self.archivo.size
            except Exception:
                pass
        super().save(*args, **kwargs)

    @property
    def tamano_legible(self):
        if not self.tamano_bytes:
            return '—'
        kb = self.tamano_bytes / 1024
        if kb < 1024:
            return f'{kb:.1f} KB'
        return f'{kb / 1024:.1f} MB'

    @property
    def extension(self):
        if self.archivo:
            return os.path.splitext(self.archivo.name)[1].lower()
        return ''

    @property
    def es_imagen(self):
        return self.extension in ['.jpg', '.jpeg', '.png']

    @property
    def es_pdf(self):
        return self.extension == '.pdf'

    def verificar(self, usuario):
        """Marca el documento como verificado."""
        from django.utils import timezone as tz
        self.estado = self.ESTADO_VERIFICADO
        self.verificado_por = usuario
        self.fecha_verificacion = tz.now()
        self.observacion = ''
        self.save()

    def rechazar(self, usuario, observacion):
        """Rechaza el documento con observación."""
        if not observacion:
            raise ValidationError('Debe indicar el motivo del rechazo.')
        self.estado = self.ESTADO_RECHAZADO
        self.verificado_por = usuario
        self.observacion = observacion
        self.save()
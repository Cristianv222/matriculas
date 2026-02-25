"""
============================================================
  MÓDULO: core
  Modelos abstractos base para todo el sistema
============================================================
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstracto con auditoría completa.
    Todos los modelos del sistema deben heredar de este.
    """
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at  = models.DateTimeField(auto_now=True,     verbose_name='Modificado el')
    is_active   = models.BooleanField(default=True,       verbose_name='Activo')

    class Meta:
        abstract = True
        ordering = ['-created_at']


class ConfiguracionSistema(TimeStampedModel):
    """
    Tabla de configuración clave-valor para parámetros del sistema
    que pueden cambiar sin necesidad de redesplegar.
    Ejemplos: 'max_documentos_mb', 'dias_vigencia_matricula', etc.
    """
    clave       = models.CharField(max_length=100, unique=True, verbose_name='Clave')
    valor       = models.TextField(verbose_name='Valor')
    descripcion = models.CharField(max_length=255, blank=True, verbose_name='Descripción')
    tipo        = models.CharField(
        max_length=20,
        choices=[
            ('texto',    'Texto'),
            ('numero',   'Número'),
            ('booleano', 'Booleano'),
            ('json',     'JSON'),
        ],
        default='texto',
        verbose_name='Tipo de dato'
    )

    class Meta:
        verbose_name        = 'Configuración del sistema'
        verbose_name_plural = 'Configuraciones del sistema'
        ordering            = ['clave']

    def __str__(self):
        return f'{self.clave} = {self.valor}'

    @classmethod
    def obtener(cls, clave, default=None):
        """Obtiene el valor de una configuración por su clave."""
        try:
            return cls.objects.get(clave=clave, is_active=True).valor
        except cls.DoesNotExist:
            return default
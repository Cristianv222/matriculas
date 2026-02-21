"""
Modelos abstractos base para todos los mÃ³dulos
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    Modelo abstracto con campos de auditorÃ­a.
    Todos los modelos del sistema heredan de este.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creaciÃ³n')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ãšltima modificaciÃ³n')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        abstract = True
        ordering = ['-created_at']

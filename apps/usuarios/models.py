"""
Modelo de Usuario personalizado con roles
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario del sistema con roles diferenciados
    """
    ROL_ADMIN = 'ADMIN'
    ROL_SECRETARIA = 'SECRETARIA'
    ROL_REPRESENTANTE = 'REPRESENTANTE'
    ROL_DOCENTE = 'DOCENTE'

    ROLES = [
        (ROL_ADMIN, 'Administrador'),
        (ROL_SECRETARIA, 'Secretaria'),
        (ROL_REPRESENTANTE, 'Representante Legal'),
        (ROL_DOCENTE, 'Docente'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default=ROL_REPRESENTANTE, verbose_name='Rol')
    cedula = models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name='CÃ©dula')
    telefono = models.CharField(max_length=15, blank=True, verbose_name='TelÃ©fono')
    foto = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True, verbose_name='Foto')
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de nacimiento')
    direccion = models.TextField(blank=True, verbose_name='DirecciÃ³n')
    is_verified = models.BooleanField(default=False, verbose_name='Email verificado')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    @property
    def es_admin(self):
        return self.rol == self.ROL_ADMIN

    @property
    def es_secretaria(self):
        return self.rol in [self.ROL_ADMIN, self.ROL_SECRETARIA]

    @property
    def es_representante(self):
        return self.rol == self.ROL_REPRESENTANTE

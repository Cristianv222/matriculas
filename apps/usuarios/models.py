"""
============================================================
  MÓDULO: usuarios
  Modelo de usuario personalizado con roles y perfil completo
============================================================
"""
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from apps.core.models import TimeStampedModel


# ─── Validadores ────────────────────────────────────────────────────────────────
cedula_validator = RegexValidator(
    regex=r'^\d{10,13}$',
    message='La cédula debe tener entre 10 y 13 dígitos numéricos.'
)
telefono_validator = RegexValidator(
    regex=r'^\+?[\d\s\-]{7,15}$',
    message='Ingrese un número de teléfono válido.'
)


class Usuario(AbstractUser):
    """
    Usuario del sistema con roles diferenciados.
    Reemplaza al User estándar de Django (AUTH_USER_MODEL).

    Roles:
    - ADMIN       → Acceso total
    - SECRETARIA  → Gestiona matrículas y documentos
    - REPRESENTANTE → Portal de solicitud de matrícula (padre/tutor)
    - DOCENTE     → Solo consulta listas
    """
    ROL_ADMIN          = 'ADMIN'
    ROL_SECRETARIA     = 'SECRETARIA'
    ROL_REPRESENTANTE  = 'REPRESENTANTE'
    ROL_DOCENTE        = 'DOCENTE'

    ROLES = [
        (ROL_ADMIN,         'Administrador'),
        (ROL_SECRETARIA,    'Secretaria'),
        (ROL_REPRESENTANTE, 'Representante Legal'),
        (ROL_DOCENTE,       'Docente'),
    ]

    # ─── Datos de rol y contacto ─────────────────────────────────────────────
    rol             = models.CharField(max_length=20, choices=ROLES,
                                       default=ROL_REPRESENTANTE, verbose_name='Rol')
    cedula          = models.CharField(max_length=13, unique=True,
                                       blank=True, null=True,
                                       validators=[cedula_validator],
                                       verbose_name='Cédula / Pasaporte')
    telefono        = models.CharField(max_length=15, blank=True,
                                       validators=[telefono_validator],
                                       verbose_name='Teléfono')
    telefono_alt    = models.CharField(max_length=15, blank=True,
                                       verbose_name='Teléfono alternativo')

    # ─── Datos personales ────────────────────────────────────────────────────
    foto            = models.ImageField(upload_to='usuarios/fotos/%Y/',
                                        blank=True, null=True, verbose_name='Foto')
    fecha_nacimiento = models.DateField(blank=True, null=True,
                                        verbose_name='Fecha de nacimiento')
    direccion       = models.TextField(blank=True, verbose_name='Dirección domiciliaria')
    ciudad          = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    sector          = models.CharField(max_length=100, blank=True, verbose_name='Sector / Barrio')

    # ─── Estado de la cuenta ─────────────────────────────────────────────────
    is_verified          = models.BooleanField(default=False, verbose_name='Email verificado')
    token_verificacion   = models.CharField(max_length=64, blank=True,
                                            verbose_name='Token de verificación de email')
    token_expiracion     = models.DateTimeField(blank=True, null=True,
                                                verbose_name='Expiración del token')
    ultimo_acceso_ip     = models.GenericIPAddressField(blank=True, null=True,
                                                        verbose_name='Última IP de acceso')

    class Meta:
        verbose_name        = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering            = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_rol_display()})'

    # ─── Propiedades de rol ───────────────────────────────────────────────────

    @property
    def es_admin(self):
        """Superusuario y rol ADMIN tienen acceso total."""
        return self.is_superuser or self.rol == self.ROL_ADMIN

    @property
    def es_secretaria(self):
        """Secretaria, Admin y superusuario pueden gestionar matrículas."""
        return self.is_superuser or self.rol in [self.ROL_ADMIN, self.ROL_SECRETARIA]

    @property
    def es_representante(self):
        """Solo usuarios con rol REPRESENTANTE que no sean superusuario."""
        return not self.is_superuser and self.rol == self.ROL_REPRESENTANTE

    @property
    def es_docente(self):
        """Solo usuarios con rol DOCENTE que no sean superusuario."""
        return not self.is_superuser and self.rol == self.ROL_DOCENTE

    @property
    def nombre_completo(self):
        return self.get_full_name() or self.username


class SesionUsuario(models.Model):
    """
    Registro de sesiones de usuarios para auditoría de seguridad.
    Se crea un registro en cada inicio de sesión.
    """
    usuario     = models.ForeignKey(Usuario, on_delete=models.CASCADE,
                                    related_name='sesiones')
    ip          = models.GenericIPAddressField(verbose_name='Dirección IP')
    user_agent  = models.TextField(blank=True, verbose_name='Navegador / Dispositivo')
    fecha_login = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de ingreso')
    fecha_logout = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de salida')
    exitosa     = models.BooleanField(default=True, verbose_name='Sesión exitosa')

    class Meta:
        verbose_name        = 'Sesión de usuario'
        verbose_name_plural = 'Sesiones de usuarios'
        ordering            = ['-fecha_login']

    def __str__(self):
        return f'{self.usuario.username} - {self.ip} - {self.fecha_login:%Y-%m-%d %H:%M}'
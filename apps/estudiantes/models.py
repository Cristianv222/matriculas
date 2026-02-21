"""
Modelo principal del Estudiante
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.usuarios.models import Usuario


class Estudiante(TimeStampedModel):
    GENERO_MASCULINO = 'M'
    GENERO_FEMENINO = 'F'
    GENERO_OTRO = 'O'
    GENEROS = [(GENERO_MASCULINO, 'Masculino'), (GENERO_FEMENINO, 'Femenino'), (GENERO_OTRO, 'Otro')]

    TIPO_SANGRE = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]

    # Datos personales
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')
    cedula = models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name='CÃ©dula')
    fecha_nacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    genero = models.CharField(max_length=1, choices=GENEROS, verbose_name='GÃ©nero')
    nacionalidad = models.CharField(max_length=50, default='Ecuatoriana', verbose_name='Nacionalidad')
    etnia = models.CharField(max_length=50, blank=True, verbose_name='Etnia/Auto-identificaciÃ³n')
    foto = models.ImageField(upload_to='estudiantes/fotos/', blank=True, null=True, verbose_name='Foto carnet')

    # Datos mÃ©dicos
    tipo_sangre = models.CharField(max_length=3, choices=TIPO_SANGRE, blank=True, verbose_name='Tipo de sangre')
    alergias = models.TextField(blank=True, verbose_name='Alergias conocidas')
    tiene_discapacidad = models.BooleanField(default=False, verbose_name='Tiene discapacidad')
    tipo_discapacidad = models.CharField(max_length=100, blank=True, verbose_name='Tipo de discapacidad')
    porcentaje_discapacidad = models.PositiveIntegerField(blank=True, null=True, verbose_name='% Discapacidad')
    numero_conadis = models.CharField(max_length=20, blank=True, verbose_name='NÂ° CONADIS')

    # Representante legal
    representante = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='estudiantes',
        verbose_name='Representante legal'
    )
    relacion_representante = models.CharField(
        max_length=50,
        default='Padre/Madre',
        verbose_name='RelaciÃ³n con el estudiante'
    )

    # Procedencia acadÃ©mica
    institucion_anterior = models.CharField(max_length=200, blank=True, verbose_name='InstituciÃ³n anterior')
    grado_anterior = models.CharField(max_length=50, blank=True, verbose_name='Ãšltimo grado aprobado')

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"

    @property
    def nombre_completo(self):
        return f"{self.apellidos} {self.nombres}"

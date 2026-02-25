"""
============================================================
  MÓDULO: estudiantes
  Ficha completa del estudiante y datos familiares
============================================================
"""
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.usuarios.models import Usuario


# ─── Validadores ─────────────────────────────────────────────────────────────
cedula_validator = RegexValidator(
    regex=r'^\d{10,13}$',
    message='La cédula debe tener entre 10 y 13 dígitos.'
)

telefono_validator = RegexValidator(
    regex=r'^\+?[\d\s\-]{7,15}$',
    message='Ingrese un número de teléfono válido.'
)


class Estudiante(TimeStampedModel):
    """
    Ficha completa del estudiante con datos personales,
    médicos, familiares y procedencia académica.
    """

    # ── Género ────────────────────────────────────────────────────────────────
    GENERO_MASCULINO = 'M'
    GENERO_FEMENINO  = 'F'
    GENERO_OTRO      = 'O'
    GENEROS = [
        (GENERO_MASCULINO, 'Masculino'),
        (GENERO_FEMENINO,  'Femenino'),
        (GENERO_OTRO,      'Prefiero no decir'),
    ]

    # ── Tipo sangre ───────────────────────────────────────────────────────────
    TIPO_SANGRE = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('', 'Desconocido'),
    ]

    # ── Auto-identificación étnica (MINEDUC Ecuador) ──────────────────────────
    ETNIA_CHOICES = [
        ('MESTIZO',        'Mestizo/a'),
        ('INDIGENA',       'Indígena'),
        ('AFROECUATORIANO','Afroecuatoriano/a'),
        ('MONTUBIO',       'Montubio/a'),
        ('BLANCO',         'Blanco/a'),
        ('MULATO',         'Mulato/a'),
        ('OTRO',           'Otro'),
        ('NO_DECLARA',     'No declara'),
    ]

    # ── Estado civil ──────────────────────────────────────────────────────────
    ESTADO_CIVIL_PADRE = [
        ('', '---'),
        ('CASADO',      'Casado'),
        ('DIVORCIADO',  'Divorciado'),
        ('VIUDO',       'Viudo'),
        ('UNION_LIBRE', 'Unión libre'),
        ('SOLTERO',     'Soltero'),
    ]
    ESTADO_CIVIL_MADRE = [
        ('', '---'),
        ('CASADA',      'Casada'),
        ('DIVORCIADA',  'Divorciada'),
        ('VIUDA',       'Viuda'),
        ('UNION_LIBRE', 'Unión libre'),
        ('SOLTERA',     'Soltera'),
    ]

    # ── Nivel de instrucción ──────────────────────────────────────────────────
    NIVEL_INSTRUCCION = [
        ('',          '---'),
        ('NINGUNA',   'Ninguna'),
        ('PRIMARIA',  'Primaria'),
        ('SECUNDARIA','Secundaria'),
        ('SUPERIOR',  'Superior'),
        ('POSGRADO',  'Posgrado'),
    ]

    # ─── Datos de identidad ──────────────────────────────────────────────────
    nombres          = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos        = models.CharField(max_length=100, verbose_name='Apellidos')
    cedula           = models.CharField(
                           max_length=13, unique=True,
                           blank=True, null=True,
                           validators=[cedula_validator],
                           verbose_name='Cédula de identidad',
                           help_text='10 dígitos para ecuatorianos, hasta 13 para pasaporte/extranjero')
    fecha_nacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    genero           = models.CharField(max_length=1, choices=GENEROS, verbose_name='Género')
    nacionalidad     = models.CharField(max_length=60, default='Ecuatoriana',
                                        verbose_name='Nacionalidad')
    etnia            = models.CharField(max_length=20, choices=ETNIA_CHOICES,
                                        default='MESTIZO',
                                        verbose_name='Auto-identificación étnica')
    lugar_nacimiento = models.CharField(max_length=100, blank=True,
                                        verbose_name='Lugar de nacimiento')
    foto             = models.ImageField(upload_to='estudiantes/fotos/%Y/',
                                        blank=True, null=True,
                                        verbose_name='Foto carnet')

    # ─── Dirección ───────────────────────────────────────────────────────────
    direccion           = models.TextField(blank=True, verbose_name='Dirección domiciliaria')
    ciudad              = models.CharField(max_length=100, blank=True, default='',
                                           verbose_name='Ciudad')
    sector              = models.CharField(max_length=100, blank=True, verbose_name='Sector / Barrio')
    telefono_emergencia = models.CharField(max_length=15, blank=True,
                                           validators=[telefono_validator],
                                           verbose_name='Teléfono de emergencia')
    contacto_emergencia = models.CharField(max_length=100, blank=True,
                                           verbose_name='Nombre del contacto de emergencia')

    # ─── Datos médicos ────────────────────────────────────────────────────────
    tipo_sangre           = models.CharField(max_length=3, choices=TIPO_SANGRE,
                                             blank=True, verbose_name='Tipo de sangre')
    alergias              = models.TextField(blank=True, verbose_name='Alergias conocidas',
                                             help_text='Describa las alergias. Deje vacío si no tiene.')
    enfermedades_cronicas = models.TextField(blank=True, verbose_name='Enfermedades crónicas',
                                             help_text='Ej: diabetes, asma, epilepsia')
    medicacion_actual     = models.TextField(blank=True, verbose_name='Medicación actual',
                                             help_text='Medicamentos que toma regularmente')
    medico_tratante       = models.CharField(max_length=100, blank=True,
                                             verbose_name='Médico tratante')
    seguro_medico         = models.CharField(max_length=100, blank=True,
                                             verbose_name='Seguro médico / IESS')

    # ─── Discapacidad ─────────────────────────────────────────────────────────
    tiene_discapacidad      = models.BooleanField(default=False,
                                                  verbose_name='Tiene discapacidad')
    tipo_discapacidad       = models.CharField(max_length=100, blank=True,
                                               verbose_name='Tipo de discapacidad',
                                               help_text='Ej: visual, auditiva, motriz, intelectual')
    porcentaje_discapacidad = models.PositiveIntegerField(
                                  blank=True, null=True,
                                  validators=[MinValueValidator(1), MaxValueValidator(100)],
                                  verbose_name='Porcentaje de discapacidad (%)')
    numero_conadis          = models.CharField(max_length=20, blank=True,
                                               verbose_name='Número de carnet CONADIS')
    necesidades_especiales  = models.TextField(blank=True,
                                               verbose_name='Necesidades educativas especiales',
                                               help_text='Describa los apoyos o adaptaciones requeridas')

    # ─── Representante legal ──────────────────────────────────────────────────
    representante = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,          # FIX: blank=True para no romper el admin
        related_name='estudiantes',
        verbose_name='Representante legal'
    )
    relacion_representante = models.CharField(
        max_length=50,
        default='Padre/Madre',
        verbose_name='Relación con el estudiante',
        help_text='Ej: Padre, Madre, Abuelo/a, Tío/a, Hermano/a'
    )

    # ─── Datos familiares — Padre ─────────────────────────────────────────────
    padre_nombres      = models.CharField(max_length=150, blank=True, verbose_name='Nombres del padre')
    padre_cedula       = models.CharField(max_length=13, blank=True, verbose_name='Cédula del padre')
    padre_ocupacion    = models.CharField(max_length=100, blank=True, verbose_name='Ocupación del padre')
    padre_telefono     = models.CharField(max_length=15, blank=True,
                                          validators=[telefono_validator],
                                          verbose_name='Teléfono del padre')
    padre_email        = models.EmailField(blank=True, verbose_name='Email del padre')
    padre_estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_PADRE,
                                          blank=True, verbose_name='Estado civil del padre')
    padre_instruccion  = models.CharField(max_length=20, choices=NIVEL_INSTRUCCION,
                                          blank=True, verbose_name='Nivel de instrucción del padre')

    # ─── Datos familiares — Madre ─────────────────────────────────────────────
    madre_nombres      = models.CharField(max_length=150, blank=True, verbose_name='Nombres de la madre')
    madre_cedula       = models.CharField(max_length=13, blank=True, verbose_name='Cédula de la madre')
    madre_ocupacion    = models.CharField(max_length=100, blank=True, verbose_name='Ocupación de la madre')
    madre_telefono     = models.CharField(max_length=15, blank=True,
                                          validators=[telefono_validator],
                                          verbose_name='Teléfono de la madre')
    madre_email        = models.EmailField(blank=True, verbose_name='Email de la madre')
    madre_estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_MADRE,
                                          blank=True, verbose_name='Estado civil de la madre')
    madre_instruccion  = models.CharField(max_length=20, choices=NIVEL_INSTRUCCION,
                                          blank=True, verbose_name='Nivel de instrucción de la madre')

    # ─── Procedencia académica ────────────────────────────────────────────────
    institucion_anterior = models.CharField(max_length=200, blank=True,
                               verbose_name='Institución educativa anterior')
    amie_anterior        = models.CharField(max_length=20, blank=True,
                               verbose_name='Código AMIE de la institución anterior')
    grado_anterior       = models.CharField(max_length=50, blank=True,
                               verbose_name='Último grado/año aprobado')
    anio_anterior        = models.CharField(max_length=9, blank=True,
                               verbose_name='Año lectivo anterior',
                               help_text='Ej: 2023-2024')
    promedio_anterior    = models.DecimalField(
                               max_digits=4, decimal_places=2,
                               blank=True, null=True,
                               validators=[MinValueValidator(0), MaxValueValidator(10)],
                               verbose_name='Promedio final año anterior')
    motivo_cambio        = models.TextField(blank=True,
                               verbose_name='Motivo de cambio de institución')

    # ─── Observaciones ────────────────────────────────────────────────────────
    observaciones_generales = models.TextField(
        blank=True,
        verbose_name='Observaciones generales',
        help_text='Información adicional relevante para el proceso de matrícula'
    )

    class Meta:
        verbose_name        = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering            = ['apellidos', 'nombres']
        indexes             = [
            models.Index(fields=['cedula']),
            models.Index(fields=['apellidos', 'nombres']),
        ]

    def __str__(self):
        return self.nombre_completo

    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}

        # Validar cédula ecuatoriana (módulo 10)
        if self.cedula and len(self.cedula) == 10:
            if not self._validar_cedula_ecuatoriana(self.cedula):
                errors['cedula'] = 'La cédula ecuatoriana ingresada no es válida.'

        # Discapacidad: si marca discapacidad, debe especificar tipo
        if self.tiene_discapacidad and not self.tipo_discapacidad:
            errors['tipo_discapacidad'] = 'Debe especificar el tipo de discapacidad.'

        # Fecha de nacimiento: no puede ser futura ni mayor a 30 años para estudiante escolar
        if self.fecha_nacimiento:
            hoy = timezone.now().date()
            if self.fecha_nacimiento > hoy:
                errors['fecha_nacimiento'] = 'La fecha de nacimiento no puede ser una fecha futura.'
            edad = self._calcular_edad(self.fecha_nacimiento)
            if edad is not None and (edad < 2 or edad > 30):
                errors['fecha_nacimiento'] = f'La edad calculada ({edad} años) parece incorrecta para un estudiante.'

        if errors:
            raise ValidationError(errors)

    @staticmethod
    def _validar_cedula_ecuatoriana(cedula: str) -> bool:
        """Validación del dígito verificador de cédulas ecuatorianas."""
        try:
            coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
            total = 0
            for i, coef in enumerate(coeficientes):
                valor = int(cedula[i]) * coef
                total += valor - 9 if valor > 9 else valor
            digito_verificador = (10 - (total % 10)) % 10
            return digito_verificador == int(cedula[9])
        except (ValueError, IndexError):
            return False

    @staticmethod
    def _calcular_edad(fecha_nacimiento) -> int | None:
        if not fecha_nacimiento:
            return None
        hoy = timezone.now().date()
        return hoy.year - fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )

    # ─── Propiedades ──────────────────────────────────────────────────────────
    @property
    def nombre_completo(self):
        return f'{self.apellidos} {self.nombres}'

    @property
    def edad(self):
        """Calcula la edad actual del estudiante."""
        return self._calcular_edad(self.fecha_nacimiento)

    @property
    def requiere_atencion_especial(self):
        return (
            self.tiene_discapacidad
            or bool(self.enfermedades_cronicas)
            or bool(self.alergias)
        )

    @property
    def tiene_datos_medicos(self):
        return bool(
            self.tipo_sangre or self.alergias or self.enfermedades_cronicas
            or self.medicacion_actual or self.medico_tratante
        )
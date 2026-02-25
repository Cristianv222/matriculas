"""
============================================================
  MÓDULO: periodos
  Años lectivos, niveles educativos, paralelos y cupos
============================================================
"""
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class PeriodoAcademico(TimeStampedModel):
    """
    Año lectivo (ej: 2024-2025 Sierra).
    Solo uno puede estar activo a la vez.
    Controla las fechas de matrícula habilitadas.
    """
    REGIMEN_SIERRA  = 'SIERRA'
    REGIMEN_COSTA   = 'COSTA'
    REGIMENES = [
        (REGIMEN_SIERRA, 'Sierra'),
        (REGIMEN_COSTA,  'Costa / Galápagos'),
    ]

    nombre                   = models.CharField(max_length=100, unique=True,
                                                verbose_name='Nombre del período',
                                                help_text='Ej: 2024-2025 Sierra')
    regimen                  = models.CharField(max_length=10, choices=REGIMENES,
                                                default=REGIMEN_SIERRA, verbose_name='Régimen')
    fecha_inicio             = models.DateField(verbose_name='Inicio de clases')
    fecha_fin                = models.DateField(verbose_name='Fin del año lectivo')

    # ─── Ventana de matrículas ───────────────────────────────────────────────
    fecha_inicio_matriculas  = models.DateField(verbose_name='Inicio de matrículas')
    fecha_fin_matriculas     = models.DateField(verbose_name='Fin de matrículas')

    # ─── Matrículas extraordinarias ──────────────────────────────────────────
    permite_matricula_extra  = models.BooleanField(default=False,
                                                   verbose_name='Permite matrícula extraordinaria')
    fecha_inicio_extra       = models.DateField(blank=True, null=True,
                                                verbose_name='Inicio matrículas extraordinarias')
    fecha_fin_extra          = models.DateField(blank=True, null=True,
                                                verbose_name='Fin matrículas extraordinarias')

    es_activo                = models.BooleanField(default=False,
                                                   verbose_name='Período activo',
                                                   help_text='Solo un período puede estar activo a la vez')
    observaciones            = models.TextField(blank=True, verbose_name='Observaciones')

    class Meta:
        verbose_name        = 'Período Académico'
        verbose_name_plural = 'Períodos Académicos'
        ordering            = ['-fecha_inicio']

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio >= self.fecha_fin:
                raise ValidationError('La fecha de inicio debe ser anterior al fin del año lectivo.')
        if self.fecha_inicio_matriculas and self.fecha_fin_matriculas:
            if self.fecha_inicio_matriculas >= self.fecha_fin_matriculas:
                raise ValidationError('La fecha de inicio de matrículas debe ser anterior al fin.')

    def save(self, *args, **kwargs):
        # Solo un período puede estar activo a la vez
        if self.es_activo:
            PeriodoAcademico.objects.exclude(pk=self.pk).update(es_activo=False)
        super().save(*args, **kwargs)

    @property
    def matriculas_abiertas(self):
        if not self.fecha_inicio_matriculas or not self.fecha_fin_matriculas:
            return False
        hoy = timezone.now().date()
        return self.fecha_inicio_matriculas <= hoy <= self.fecha_fin_matriculas

    @property
    def matriculas_extraordinarias_abiertas(self):
        if not self.permite_matricula_extra:
            return False
        if not self.fecha_inicio_extra or not self.fecha_fin_extra:
            return False
        hoy = timezone.now().date()
        return self.fecha_inicio_extra <= hoy <= self.fecha_fin_extra

    @property
    def puede_matricular(self):
        return self.matriculas_abiertas or self.matriculas_extraordinarias_abiertas

    @classmethod
    def get_activo(cls):
        """Retorna el período académico activo o None."""
        return cls.objects.filter(es_activo=True, is_active=True).first()


class Nivel(TimeStampedModel):
    """
    Grado o curso educativo.
    Ej: 1ro EGB, 2do EGB, ... 10mo EGB, 1ro BGU, 2do BGU, 3ro BGU
    """
    SUBNIVEL_PREPARATORIA     = 'PREPARATORIA'
    SUBNIVEL_BASICA_ELEMENTAL = 'BASICA_ELEMENTAL'
    SUBNIVEL_BASICA_MEDIA     = 'BASICA_MEDIA'
    SUBNIVEL_BASICA_SUPERIOR  = 'BASICA_SUPERIOR'
    SUBNIVEL_BGU              = 'BGU'

    SUBNIVELES = [
        (SUBNIVEL_PREPARATORIA,      'Preparatoria (1ro EGB)'),
        (SUBNIVEL_BASICA_ELEMENTAL,  'Básica Elemental (2do-4to EGB)'),
        (SUBNIVEL_BASICA_MEDIA,      'Básica Media (5to-7mo EGB)'),
        (SUBNIVEL_BASICA_SUPERIOR,   'Básica Superior (8vo-10mo EGB)'),
        (SUBNIVEL_BGU,               'Bachillerato General Unificado (BGU)'),
    ]

    nombre      = models.CharField(max_length=100, verbose_name='Nombre del nivel',
                                   help_text='Ej: 1ro EGB, 8vo EGB, 2do BGU')
    # ✅ CORREGIDO: se agrega default para evitar el prompt interactivo en makemigrations
    subnivel    = models.CharField(max_length=20, choices=SUBNIVELES,
                                   default=SUBNIVEL_BASICA_ELEMENTAL,
                                   verbose_name='Sub-nivel educativo')
    orden       = models.PositiveIntegerField(verbose_name='Orden de visualización',
                                              help_text='1 para primero, 13 para 3ro BGU')
    descripcion = models.CharField(max_length=200, blank=True, verbose_name='Descripción adicional')

    class Meta:
        verbose_name        = 'Nivel'
        verbose_name_plural = 'Niveles'
        ordering            = ['orden']

    def __str__(self):
        return self.nombre


class Paralelo(TimeStampedModel):
    """
    Paralelo de un nivel en un período académico.
    Ej: 3ro EGB Paralelo A - Período 2024-2025.
    Controla el cupo disponible en tiempo real.
    """
    periodo      = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE,
                                     related_name='paralelos',
                                     verbose_name='Período académico')
    nivel        = models.ForeignKey(Nivel, on_delete=models.CASCADE,
                                     related_name='paralelos',
                                     verbose_name='Nivel / Grado')
    nombre       = models.CharField(max_length=5, verbose_name='Identificador del paralelo',
                                    help_text='Ej: A, B, C')
    cupo_maximo  = models.PositiveIntegerField(default=35,
                                               validators=[MinValueValidator(1), MaxValueValidator(60)],
                                               verbose_name='Cupo máximo de estudiantes')
    jornada      = models.CharField(max_length=20,
                                    choices=[('MATUTINA', 'Matutina'),
                                             ('VESPERTINA', 'Vespertina'),
                                             ('NOCTURNA', 'Nocturna')],
                                    default='MATUTINA',
                                    verbose_name='Jornada')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')

    class Meta:
        verbose_name        = 'Paralelo'
        verbose_name_plural = 'Paralelos'
        unique_together     = [['periodo', 'nivel', 'nombre']]
        ordering            = ['nivel__orden', 'nombre']

    def __str__(self):
        return f'{self.nivel} - Paralelo {self.nombre} ({self.periodo})'

    @property
    def matriculados_aprobados(self):
        """Número de estudiantes con matrícula APROBADA en este paralelo."""
        from apps.matriculas.models import Matricula
        return Matricula.objects.filter(
            paralelo=self,
            estado=Matricula.ESTADO_APROBADA,
            is_active=True
        ).count()

    @property
    def cupo_disponible(self):
        return max(0, self.cupo_maximo - self.matriculados_aprobados)

    @property
    def cupo_lleno(self):
        return self.cupo_disponible <= 0

    @property
    def porcentaje_ocupacion(self):
        if self.cupo_maximo == 0:
            return 0
        return round((self.matriculados_aprobados / self.cupo_maximo) * 100, 1)
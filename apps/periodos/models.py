"""
PerÃ­odos acadÃ©micos, niveles, paralelos y cupos
"""
from django.db import models
from apps.core.models import TimeStampedModel


class PeriodoAcademico(TimeStampedModel):
    """AÃ±o lectivo (ej: 2024-2025 Sierra)"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre del perÃ­odo')
    fecha_inicio = models.DateField(verbose_name='Inicio de clases')
    fecha_fin = models.DateField(verbose_name='Fin de clases')
    fecha_inicio_matriculas = models.DateField(verbose_name='Inicio matrÃ­culas')
    fecha_fin_matriculas = models.DateField(verbose_name='Fin matrÃ­culas')
    es_activo = models.BooleanField(default=False, verbose_name='PerÃ­odo activo')

    class Meta:
        verbose_name = 'PerÃ­odo AcadÃ©mico'
        verbose_name_plural = 'PerÃ­odos AcadÃ©micos'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Solo un perÃ­odo puede estar activo a la vez
        if self.es_activo:
            PeriodoAcademico.objects.exclude(pk=self.pk).update(es_activo=False)
        super().save(*args, **kwargs)


class Nivel(TimeStampedModel):
    """Grado/Curso (ej: 1ro EGB, 10mo EGB, 1ro BGU)"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre del nivel')
    orden = models.PositiveIntegerField(verbose_name='Orden de visualizaciÃ³n')
    descripcion = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Nivel'
        verbose_name_plural = 'Niveles'
        ordering = ['orden']

    def __str__(self):
        return self.nombre


class Paralelo(TimeStampedModel):
    """Paralelo de un nivel en un perÃ­odo (ej: 3ro A - 2024)"""
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE, related_name='paralelos')
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='paralelos')
    nombre = models.CharField(max_length=10, verbose_name='Paralelo (A, B, C...)')
    cupo_maximo = models.PositiveIntegerField(default=35, verbose_name='Cupo mÃ¡ximo')

    class Meta:
        verbose_name = 'Paralelo'
        verbose_name_plural = 'Paralelos'
        unique_together = [['periodo', 'nivel', 'nombre']]
        ordering = ['nivel__orden', 'nombre']

    def __str__(self):
        return f"{self.nivel} - Paralelo {self.nombre} ({self.periodo})"

    @property
    def cupo_disponible(self):
        from apps.matriculas.models import Matricula
        ocupados = Matricula.objects.filter(
            paralelo=self,
            estado=Matricula.ESTADO_APROBADA
        ).count()
        return self.cupo_maximo - ocupados

    @property
    def cupo_lleno(self):
        return self.cupo_disponible <= 0

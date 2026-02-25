"""
============================================================
  MÓDULO: periodos — serializers.py
============================================================
"""
from rest_framework import serializers
from .models import PeriodoAcademico, Nivel, Paralelo


class NivelSerializer(serializers.ModelSerializer):
    subnivel_display = serializers.CharField(source='get_subnivel_display', read_only=True)

    class Meta:
        model  = Nivel
        fields = ['id', 'nombre', 'subnivel', 'subnivel_display', 'orden', 'descripcion']


class PeriodoAcademicoSerializer(serializers.ModelSerializer):
    regimen_display                    = serializers.CharField(source='get_regimen_display', read_only=True)
    matriculas_abiertas                = serializers.ReadOnlyField()
    matriculas_extraordinarias_abiertas = serializers.ReadOnlyField()
    puede_matricular                   = serializers.ReadOnlyField()

    class Meta:
        model  = PeriodoAcademico
        fields = [
            'id', 'nombre', 'regimen', 'regimen_display',
            'fecha_inicio', 'fecha_fin',
            'fecha_inicio_matriculas', 'fecha_fin_matriculas',
            'permite_matricula_extra', 'fecha_inicio_extra', 'fecha_fin_extra',
            'es_activo', 'observaciones',
            'matriculas_abiertas', 'matriculas_extraordinarias_abiertas', 'puede_matricular',
        ]

    def validate(self, attrs):
        fi  = attrs.get('fecha_inicio')
        ff  = attrs.get('fecha_fin')
        fim = attrs.get('fecha_inicio_matriculas')
        ffm = attrs.get('fecha_fin_matriculas')

        if fi and ff and fi >= ff:
            raise serializers.ValidationError(
                {'fecha_fin': 'El fin del año lectivo debe ser posterior al inicio.'}
            )
        if fim and ffm and fim >= ffm:
            raise serializers.ValidationError(
                {'fecha_fin_matriculas': 'El fin de matrículas debe ser posterior al inicio.'}
            )
        return attrs


class ParaleloSerializer(serializers.ModelSerializer):
    """Serializer compacto para listados y selects."""
    nivel_nombre   = serializers.CharField(source='nivel.nombre',   read_only=True)
    periodo_nombre = serializers.CharField(source='periodo.nombre', read_only=True)
    jornada_display = serializers.CharField(source='get_jornada_display', read_only=True)

    class Meta:
        model  = Paralelo
        fields = [
            'id', 'periodo', 'periodo_nombre',
            'nivel', 'nivel_nombre',
            'nombre', 'jornada', 'jornada_display', 'cupo_maximo',
        ]


class ParaleloDetalleSerializer(ParaleloSerializer):
    """Serializer completo que incluye cupo en tiempo real."""
    matriculados_aprobados = serializers.ReadOnlyField()
    cupo_disponible        = serializers.ReadOnlyField()
    cupo_lleno             = serializers.ReadOnlyField()
    porcentaje_ocupacion   = serializers.ReadOnlyField()
    nivel_detalle          = NivelSerializer(source='nivel', read_only=True)

    class Meta(ParaleloSerializer.Meta):
        fields = ParaleloSerializer.Meta.fields + [
            'matriculados_aprobados', 'cupo_disponible',
            'cupo_lleno', 'porcentaje_ocupacion',
            'nivel_detalle', 'observaciones',
        ]
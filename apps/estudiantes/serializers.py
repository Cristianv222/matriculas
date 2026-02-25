"""
============================================================
  MÓDULO: estudiantes — serializers.py
  Requiere: pip install djangorestframework
============================================================
"""
from rest_framework import serializers
from .models import Estudiante


class EstudianteListSerializer(serializers.ModelSerializer):
    """Serializer compacto para listados."""
    nombre_completo     = serializers.ReadOnlyField()
    edad                = serializers.ReadOnlyField()
    representante_str   = serializers.StringRelatedField(source='representante')
    requiere_atencion   = serializers.ReadOnlyField(source='requiere_atencion_especial')

    class Meta:
        model  = Estudiante
        fields = [
            'id', 'nombre_completo', 'cedula', 'edad', 'genero',
            'ciudad', 'representante_str', 'requiere_atencion', 'foto',
        ]


class EstudianteSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle / creación / edición."""
    nombre_completo          = serializers.ReadOnlyField()
    edad                     = serializers.ReadOnlyField()
    requiere_atencion_especial = serializers.ReadOnlyField()
    tiene_datos_medicos      = serializers.ReadOnlyField()
    genero_display           = serializers.CharField(source='get_genero_display', read_only=True)
    etnia_display            = serializers.CharField(source='get_etnia_display',  read_only=True)

    class Meta:
        model  = Estudiante
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_cedula(self, value):
        if value and len(value) == 10:
            if not Estudiante._validar_cedula_ecuatoriana(value):
                raise serializers.ValidationError('La cédula ecuatoriana no es válida.')
        return value

    def validate(self, attrs):
        if attrs.get('tiene_discapacidad') and not attrs.get('tipo_discapacidad'):
            raise serializers.ValidationError({
                'tipo_discapacidad': 'Debe especificar el tipo de discapacidad.'
            })
        return attrs
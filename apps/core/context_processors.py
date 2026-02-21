"""
Context processors: datos globales disponibles en todos los templates
"""
from django.conf import settings


def school_info(request):
    return {
        'SCHOOL_NAME': getattr(settings, 'SCHOOL_NAME', 'San Francisco de Quito'),
        'SCHOOL_AMIE': getattr(settings, 'SCHOOL_AMIE', ''),
        'SCHOOL_CITY': getattr(settings, 'SCHOOL_CITY', 'Quito'),
        'SCHOOL_PROVINCE': getattr(settings, 'SCHOOL_PROVINCE', 'Pichincha'),
    }

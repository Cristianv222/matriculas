"""
ConfiguraciÃ³n de DESARROLLO
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Email en consola durante desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar (opcional)
INSTALLED_APPS += ['debug_toolbar'] if False else []

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

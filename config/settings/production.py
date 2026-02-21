"""
ConfiguraciÃ³n de PRODUCCIÃ“N
"""
from .base import *
from decouple import config

DEBUG = False
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='').split(',')

# Email SMTP real
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')

SECURE_SSL_REDIRECT = False  # Activar cuando tengas HTTPS
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'WARNING',
    },
}

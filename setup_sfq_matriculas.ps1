# ============================================================
#  SCRIPT DE CREACIÓN DE PROYECTO - SFQ MATRICULAS
#  Escuela San Francisco de Quito - Sistema de Matrículas Online
#  Django + Docker + PostgreSQL
#  Ejecutar en PowerShell como Administrador en Windows 11
# ============================================================

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   SFQ MATRICULAS - Creando estructura del proyecto   " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# ─────────────────────────────────────────
# CONFIGURACIÓN BASE
# ─────────────────────────────────────────
$BASE_PATH = (Get-Location).Path

# ─────────────────────────────────────────
# FUNCIÓN AUXILIAR
# ─────────────────────────────────────────
function New-Dir($path) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

function New-File($path, $content = "") {
    $dir = Split-Path $path -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Set-Content -Path $path -Value $content -Encoding UTF8
}

# ─────────────────────────────────────────
# CREAR DIRECTORIOS PRINCIPALES
# ─────────────────────────────────────────
Write-Host "[1/9] Creando directorios principales..." -ForegroundColor Yellow

$dirs = @(
    "$BASE_PATH",
    "$BASE_PATH\config\settings",
    "$BASE_PATH\apps\core\migrations",
    "$BASE_PATH\apps\usuarios\migrations",
    "$BASE_PATH\apps\estudiantes\migrations",
    "$BASE_PATH\apps\periodos\migrations",
    "$BASE_PATH\apps\matriculas\migrations",
    "$BASE_PATH\apps\documentos\migrations",
    "$BASE_PATH\apps\notificaciones\migrations",
    "$BASE_PATH\apps\reportes\migrations",
    "$BASE_PATH\templates\core",
    "$BASE_PATH\templates\usuarios",
    "$BASE_PATH\templates\estudiantes",
    "$BASE_PATH\templates\periodos",
    "$BASE_PATH\templates\matriculas",
    "$BASE_PATH\templates\documentos",
    "$BASE_PATH\templates\notificaciones",
    "$BASE_PATH\templates\reportes",
    "$BASE_PATH\static\css",
    "$BASE_PATH\static\js",
    "$BASE_PATH\static\img",
    "$BASE_PATH\media\documentos",
    "$BASE_PATH\locale",
    "$BASE_PATH\logs",
    "$BASE_PATH\nginx"
)

foreach ($dir in $dirs) { New-Dir $dir }
Write-Host "   OK - Directorios creados" -ForegroundColor Green

# ─────────────────────────────────────────
# ARCHIVOS RAÍZ DEL PROYECTO
# ─────────────────────────────────────────
Write-Host "[2/9] Creando archivos raíz (Docker, requirements, env)..." -ForegroundColor Yellow

# .env
New-File "$BASE_PATH\.env" @"
# ─────────────────────────────────────
#  VARIABLES DE ENTORNO - DESARROLLO
#  Copiar a .env.production para prod
# ─────────────────────────────────────

# Django
DJANGO_SETTINGS_MODULE=config.settings.development
DJANGO_SECRET_KEY=cambia-esta-clave-secreta-en-produccion-1234567890abcdef
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=sfq_matriculas_db
DB_USER=sfq_user
DB_PASSWORD=sfq_password_2024
DB_HOST=db
DB_PORT=5432

# Email (configurar con SMTP real en producción)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=correo@sanfranciscoquito.edu.ec
EMAIL_HOST_PASSWORD=tu_password_de_app

# Configuración de la institución
SCHOOL_NAME=Escuela Fiscomisional San Francisco de Quito
SCHOOL_AMIE=17H00000
SCHOOL_CITY=Quito
SCHOOL_PROVINCE=Pichincha
"@

# .env.example
New-File "$BASE_PATH\.env.example" @"
DJANGO_SETTINGS_MODULE=config.settings.development
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=sfq_matriculas_db
DB_USER=sfq_user
DB_PASSWORD=tu_password
DB_HOST=db
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu@email.com
EMAIL_HOST_PASSWORD=tu_password_de_app
SCHOOL_NAME=Escuela Fiscomisional San Francisco de Quito
SCHOOL_AMIE=17H00000
SCHOOL_CITY=Quito
SCHOOL_PROVINCE=Pichincha
"@

# .gitignore
New-File "$BASE_PATH\.gitignore" @"
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
*.so

# Django
*.log
local_settings.py
db.sqlite3
media/
staticfiles/

# Entorno
.env
.env.production
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Docker
*.pid

# OS
.DS_Store
Thumbs.db
"@

# requirements.txt
New-File "$BASE_PATH\requirements.txt" @"
# ─────────────────────────────────
#  DEPENDENCIAS DEL PROYECTO
# ─────────────────────────────────

# Framework principal
Django==4.2.9
djangorestframework==3.14.0

# Base de datos
psycopg2-binary==2.9.9

# Variables de entorno
python-decouple==3.8
python-dotenv==1.0.0

# Autenticación
django-allauth==0.61.1

# Formularios y UI
django-crispy-forms==2.1
crispy-bootstrap5==0.7

# Imágenes y archivos
Pillow==10.2.0

# PDF
reportlab==4.1.0
weasyprint==61.2

# Excel
openpyxl==3.1.2

# Email
django-anymail==10.2

# Utilidades
django-extensions==3.2.3
django-filter==23.5
shortuuid==1.0.13

# Seguridad
django-axes==6.3.0

# Servidor de producción
gunicorn==21.2.0
whitenoise==6.6.0

# Testing
pytest==7.4.4
pytest-django==4.7.0
factory-boy==3.3.0
"@

# Dockerfile
New-File "$BASE_PATH\Dockerfile" @"
# ─────────────────────────────────
#  DOCKERFILE - SFQ MATRICULAS
# ─────────────────────────────────
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema (necesarias para WeasyPrint y psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar proyecto
COPY . .

# Script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
"@

# docker-compose.yml
New-File "$BASE_PATH\docker-compose.yml" @"
# ─────────────────────────────────────────
#  DOCKER COMPOSE - SFQ MATRICULAS
#  Servicios: web, db, nginx
# ─────────────────────────────────────────
version: '3.9'

services:

  # ─── Base de datos PostgreSQL ───
  db:
    image: postgres:15-alpine
    container_name: sfq_db
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: \${DB_NAME}
      POSTGRES_USER: \${DB_USER}
      POSTGRES_PASSWORD: \${DB_PASSWORD}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${DB_USER} -d \${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ─── Aplicación Django ───
  web:
    build: .
    container_name: sfq_web
    restart: unless-stopped
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --reload

  # ─── Nginx (proxy reverso) ───
  nginx:
    image: nginx:alpine
    container_name: sfq_nginx
    restart: unless-stopped
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
"@

# entrypoint.sh
New-File "$BASE_PATH\entrypoint.sh" @"
#!/bin/sh
# ─────────────────────────────────────────────
#  ENTRYPOINT - Esperar DB, migrar, iniciar
# ─────────────────────────────────────────────
echo "Esperando a PostgreSQL..."
while ! nc -z \$DB_HOST \$DB_PORT; do
  sleep 0.5
done
echo "PostgreSQL listo."

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor..."
exec "\$@"
"@

# Nginx config
New-File "$BASE_PATH\nginx\nginx.conf" @"
upstream sfq_web {
    server web:8000;
}

server {
    listen 80;
    server_name localhost;
    client_max_body_size 20M;

    location / {
        proxy_pass http://sfq_web;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_redirect off;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }
}
"@

Write-Host "   OK - Archivos raíz creados" -ForegroundColor Green

# ─────────────────────────────────────────
# MANAGE.PY Y CONFIG
# ─────────────────────────────────────────
Write-Host "[3/9] Creando manage.py y configuración Django..." -ForegroundColor Yellow

New-File "$BASE_PATH\manage.py" @"
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Asegúrate de tenerlo instalado."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"@

New-File "$BASE_PATH\config\__init__.py" ""

New-File "$BASE_PATH\config\settings\__init__.py" ""

# settings/base.py
New-File "$BASE_PATH\config\settings\base.py" @"
"""
Configuración base - SFQ Matrículas
Compartida entre development y production
"""
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'django_extensions',
    'axes',
]

LOCAL_APPS = [
    'apps.core',
    'apps.usuarios',
    'apps.estudiantes',
    'apps.periodos',
    'apps.matriculas',
    'apps.documentos',
    'apps.notificaciones',
    'apps.reportes',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.school_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

AUTH_USER_MODEL = 'usuarios.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGIN_URL = '/usuarios/login/'
LOGIN_REDIRECT_URL = '/matriculas/dashboard/'
LOGOUT_REDIRECT_URL = '/usuarios/login/'

# Configuración de la institución (desde .env)
SCHOOL_NAME = config('SCHOOL_NAME', default='Escuela Fiscomisional San Francisco de Quito')
SCHOOL_AMIE = config('SCHOOL_AMIE', default='')
SCHOOL_CITY = config('SCHOOL_CITY', default='Quito')
SCHOOL_PROVINCE = config('SCHOOL_PROVINCE', default='Pichincha')

# Tamaño máximo de archivos subidos (20MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Axes - protección contra fuerza bruta
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # horas
"@

# settings/development.py
New-File "$BASE_PATH\config\settings\development.py" @"
"""
Configuración de DESARROLLO
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
"@

# settings/production.py
New-File "$BASE_PATH\config\settings\production.py" @"
"""
Configuración de PRODUCCIÓN
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
"@

# config/urls.py
New-File "$BASE_PATH\config\urls.py" @"
"""
URLs principales del proyecto SFQ Matrículas
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'SFQ Matrículas - Administración'
admin.site.site_title = 'San Francisco de Quito'
admin.site.index_title = 'Panel de Administración'

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Módulos de la aplicación
    path('', include('apps.core.urls', namespace='core')),
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('estudiantes/', include('apps.estudiantes.urls', namespace='estudiantes')),
    path('periodos/', include('apps.periodos.urls', namespace='periodos')),
    path('matriculas/', include('apps.matriculas.urls', namespace='matriculas')),
    path('documentos/', include('apps.documentos.urls', namespace='documentos')),
    path('notificaciones/', include('apps.notificaciones.urls', namespace='notificaciones')),
    path('reportes/', include('apps.reportes.urls', namespace='reportes')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"@

# config/wsgi.py
New-File "$BASE_PATH\config\wsgi.py" @"
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
application = get_wsgi_application()
"@

Write-Host "   OK - Configuración Django creada" -ForegroundColor Green

# ─────────────────────────────────────────
# MÓDULO: core
# ─────────────────────────────────────────
Write-Host "[4/9] Creando módulo core..." -ForegroundColor Yellow

New-File "$BASE_PATH\apps\__init__.py" ""
New-File "$BASE_PATH\apps\core\__init__.py" ""
New-File "$BASE_PATH\apps\core\migrations\__init__.py" ""

New-File "$BASE_PATH\apps\core\models.py" @"
"""
Modelos abstractos base para todos los módulos
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    Modelo abstracto con campos de auditoría.
    Todos los modelos del sistema heredan de este.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última modificación')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        abstract = True
        ordering = ['-created_at']
"@

New-File "$BASE_PATH\apps\core\context_processors.py" @"
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
"@

New-File "$BASE_PATH\apps\core\apps.py" @"
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
"@

New-File "$BASE_PATH\apps\core\admin.py" "from django.contrib import admin"
New-File "$BASE_PATH\apps\core\views.py" @"
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    if request.user.is_authenticated:
        return render(request, 'core/home.html')
    return render(request, 'core/landing.html')
"@

New-File "$BASE_PATH\apps\core\urls.py" @"
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
]
"@

New-File "$BASE_PATH\apps\core\utils.py" @"
"""
Utilidades compartidas del sistema
"""
import shortuuid
from django.core.mail import send_mail
from django.conf import settings


def generar_codigo_matricula():
    """Genera un código único para la matrícula"""
    return f"MAT-{shortuuid.uuid()[:8].upper()}"


def enviar_email_sistema(destinatario, asunto, mensaje):
    """Wrapper para envío de emails del sistema"""
    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@sfq.edu.ec',
        recipient_list=[destinatario],
        fail_silently=True,
    )
"@

Write-Host "   OK - Módulo core creado" -ForegroundColor Green

# ─────────────────────────────────────────
# MÓDULO: usuarios
# ─────────────────────────────────────────
Write-Host "[5/9] Creando módulo usuarios..." -ForegroundColor Yellow

New-File "$BASE_PATH\apps\usuarios\__init__.py" ""
New-File "$BASE_PATH\apps\usuarios\migrations\__init__.py" ""

New-File "$BASE_PATH\apps\usuarios\models.py" @"
"""
Modelo de Usuario personalizado con roles
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario del sistema con roles diferenciados
    """
    ROL_ADMIN = 'ADMIN'
    ROL_SECRETARIA = 'SECRETARIA'
    ROL_REPRESENTANTE = 'REPRESENTANTE'
    ROL_DOCENTE = 'DOCENTE'

    ROLES = [
        (ROL_ADMIN, 'Administrador'),
        (ROL_SECRETARIA, 'Secretaria'),
        (ROL_REPRESENTANTE, 'Representante Legal'),
        (ROL_DOCENTE, 'Docente'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default=ROL_REPRESENTANTE, verbose_name='Rol')
    cedula = models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name='Cédula')
    telefono = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')
    foto = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True, verbose_name='Foto')
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de nacimiento')
    direccion = models.TextField(blank=True, verbose_name='Dirección')
    is_verified = models.BooleanField(default=False, verbose_name='Email verificado')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    @property
    def es_admin(self):
        return self.rol == self.ROL_ADMIN

    @property
    def es_secretaria(self):
        return self.rol in [self.ROL_ADMIN, self.ROL_SECRETARIA]

    @property
    def es_representante(self):
        return self.rol == self.ROL_REPRESENTANTE
"@

New-File "$BASE_PATH\apps\usuarios\forms.py" @"
"""
Formularios del módulo de usuarios
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión personalizado"""
    username = forms.CharField(
        label='Cédula o Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su cédula'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )


class RegistroRepresentanteForm(UserCreationForm):
    """Formulario de registro para representantes legales"""
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'cedula', 'email', 'telefono', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = Usuario.ROL_REPRESENTANTE
        user.username = self.cleaned_data['cedula']
        if commit:
            user.save()
        return user
"@

New-File "$BASE_PATH\apps\usuarios\views.py" @"
"""
Vistas del módulo de usuarios
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistroRepresentanteForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'Bienvenido, {form.get_user().get_full_name()}')
        return redirect('matriculas:dashboard')
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('usuarios:login')


def registro_view(request):
    form = RegistroRepresentanteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Cuenta creada exitosamente.')
        return redirect('matriculas:dashboard')
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def perfil_view(request):
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})
"@

New-File "$BASE_PATH\apps\usuarios\urls.py" @"
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('perfil/', views.perfil_view, name='perfil'),
]
"@

New-File "$BASE_PATH\apps\usuarios\admin.py" @"
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'cedula', 'email', 'rol', 'is_active']
    list_filter = ['rol', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'cedula', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {'fields': ('rol', 'cedula', 'telefono', 'foto', 'fecha_nacimiento', 'direccion', 'is_verified')}),
    )
"@

New-File "$BASE_PATH\apps\usuarios\apps.py" @"
from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    verbose_name = 'Usuarios'
"@

Write-Host "   OK - Módulo usuarios creado" -ForegroundColor Green

# ─────────────────────────────────────────
# MÓDULO: estudiantes
# ─────────────────────────────────────────
Write-Host "[6/9] Creando módulos estudiantes, periodos y matriculas..." -ForegroundColor Yellow

New-File "$BASE_PATH\apps\estudiantes\__init__.py" ""
New-File "$BASE_PATH\apps\estudiantes\migrations\__init__.py" ""

New-File "$BASE_PATH\apps\estudiantes\models.py" @"
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
    cedula = models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name='Cédula')
    fecha_nacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    genero = models.CharField(max_length=1, choices=GENEROS, verbose_name='Género')
    nacionalidad = models.CharField(max_length=50, default='Ecuatoriana', verbose_name='Nacionalidad')
    etnia = models.CharField(max_length=50, blank=True, verbose_name='Etnia/Auto-identificación')
    foto = models.ImageField(upload_to='estudiantes/fotos/', blank=True, null=True, verbose_name='Foto carnet')

    # Datos médicos
    tipo_sangre = models.CharField(max_length=3, choices=TIPO_SANGRE, blank=True, verbose_name='Tipo de sangre')
    alergias = models.TextField(blank=True, verbose_name='Alergias conocidas')
    tiene_discapacidad = models.BooleanField(default=False, verbose_name='Tiene discapacidad')
    tipo_discapacidad = models.CharField(max_length=100, blank=True, verbose_name='Tipo de discapacidad')
    porcentaje_discapacidad = models.PositiveIntegerField(blank=True, null=True, verbose_name='% Discapacidad')
    numero_conadis = models.CharField(max_length=20, blank=True, verbose_name='N° CONADIS')

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
        verbose_name='Relación con el estudiante'
    )

    # Procedencia académica
    institucion_anterior = models.CharField(max_length=200, blank=True, verbose_name='Institución anterior')
    grado_anterior = models.CharField(max_length=50, blank=True, verbose_name='Último grado aprobado')

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"

    @property
    def nombre_completo(self):
        return f"{self.apellidos} {self.nombres}"
"@

New-File "$BASE_PATH\apps\estudiantes\admin.py" @"
from django.contrib import admin
from .models import Estudiante


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'cedula', 'genero', 'representante', 'is_active']
    list_filter = ['genero', 'tiene_discapacidad', 'is_active']
    search_fields = ['nombres', 'apellidos', 'cedula']
    raw_id_fields = ['representante']
"@

New-File "$BASE_PATH\apps\estudiantes\views.py" @"
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Estudiante


@login_required
def lista_estudiantes(request):
    if request.user.es_secretaria:
        estudiantes = Estudiante.objects.filter(is_active=True)
    else:
        estudiantes = Estudiante.objects.filter(representante=request.user, is_active=True)
    return render(request, 'estudiantes/lista.html', {'estudiantes': estudiantes})


@login_required
def detalle_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    return render(request, 'estudiantes/detalle.html', {'estudiante': estudiante})
"@

New-File "$BASE_PATH\apps\estudiantes\urls.py" @"
from django.urls import path
from . import views

app_name = 'estudiantes'

urlpatterns = [
    path('', views.lista_estudiantes, name='lista'),
    path('<int:pk>/', views.detalle_estudiante, name='detalle'),
]
"@

New-File "$BASE_PATH\apps\estudiantes\forms.py" @"
from django import forms
from .models import Estudiante


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        exclude = ['created_at', 'updated_at', 'representante']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'tipo_sangre': forms.Select(attrs={'class': 'form-select'}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
"@

New-File "$BASE_PATH\apps\estudiantes\apps.py" @"
from django.apps import AppConfig

class EstudiantesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.estudiantes'
    verbose_name = 'Estudiantes'
"@

# ─── periodos ───
New-File "$BASE_PATH\apps\periodos\__init__.py" ""
New-File "$BASE_PATH\apps\periodos\migrations\__init__.py" ""

New-File "$BASE_PATH\apps\periodos\models.py" @"
"""
Períodos académicos, niveles, paralelos y cupos
"""
from django.db import models
from apps.core.models import TimeStampedModel


class PeriodoAcademico(TimeStampedModel):
    """Año lectivo (ej: 2024-2025 Sierra)"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre del período')
    fecha_inicio = models.DateField(verbose_name='Inicio de clases')
    fecha_fin = models.DateField(verbose_name='Fin de clases')
    fecha_inicio_matriculas = models.DateField(verbose_name='Inicio matrículas')
    fecha_fin_matriculas = models.DateField(verbose_name='Fin matrículas')
    es_activo = models.BooleanField(default=False, verbose_name='Período activo')

    class Meta:
        verbose_name = 'Período Académico'
        verbose_name_plural = 'Períodos Académicos'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Solo un período puede estar activo a la vez
        if self.es_activo:
            PeriodoAcademico.objects.exclude(pk=self.pk).update(es_activo=False)
        super().save(*args, **kwargs)


class Nivel(TimeStampedModel):
    """Grado/Curso (ej: 1ro EGB, 10mo EGB, 1ro BGU)"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre del nivel')
    orden = models.PositiveIntegerField(verbose_name='Orden de visualización')
    descripcion = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Nivel'
        verbose_name_plural = 'Niveles'
        ordering = ['orden']

    def __str__(self):
        return self.nombre


class Paralelo(TimeStampedModel):
    """Paralelo de un nivel en un período (ej: 3ro A - 2024)"""
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE, related_name='paralelos')
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='paralelos')
    nombre = models.CharField(max_length=10, verbose_name='Paralelo (A, B, C...)')
    cupo_maximo = models.PositiveIntegerField(default=35, verbose_name='Cupo máximo')

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
"@

New-File "$BASE_PATH\apps\periodos\admin.py" @"
from django.contrib import admin
from .models import PeriodoAcademico, Nivel, Paralelo


@admin.register(PeriodoAcademico)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_inicio', 'fecha_fin', 'es_activo']
    list_filter = ['es_activo']


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden']
    ordering = ['orden']


@admin.register(Paralelo)
class ParaleloAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'cupo_maximo', 'cupo_disponible', 'is_active']
    list_filter = ['periodo', 'nivel']
"@

New-File "$BASE_PATH\apps\periodos\views.py" @"
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PeriodoAcademico, Nivel, Paralelo


@login_required
def lista_paralelos(request):
    periodo_activo = PeriodoAcademico.objects.filter(es_activo=True).first()
    paralelos = Paralelo.objects.filter(periodo=periodo_activo, is_active=True) if periodo_activo else []
    return render(request, 'periodos/paralelos.html', {
        'periodo': periodo_activo,
        'paralelos': paralelos
    })
"@

New-File "$BASE_PATH\apps\periodos\urls.py" @"
from django.urls import path
from . import views

app_name = 'periodos'

urlpatterns = [
    path('paralelos/', views.lista_paralelos, name='paralelos'),
]
"@

New-File "$BASE_PATH\apps\periodos\apps.py" @"
from django.apps import AppConfig

class PeriodosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.periodos'
    verbose_name = 'Períodos Académicos'
"@

# ─── matriculas ───
New-File "$BASE_PATH\apps\matriculas\__init__.py" ""
New-File "$BASE_PATH\apps\matriculas\migrations\__init__.py" ""

New-File "$BASE_PATH\apps\matriculas\models.py" @"
"""
Modelo principal del proceso de matrícula
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.usuarios.models import Usuario
from apps.estudiantes.models import Estudiante
from apps.periodos.models import Paralelo


class Matricula(TimeStampedModel):
    """
    Solicitud y proceso completo de matrícula
    """
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_EN_REVISION = 'EN_REVISION'
    ESTADO_APROBADA = 'APROBADA'
    ESTADO_RECHAZADA = 'RECHAZADA'
    ESTADO_ANULADA = 'ANULADA'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente de revisión'),
        (ESTADO_EN_REVISION, 'En revisión'),
        (ESTADO_APROBADA, 'Aprobada'),
        (ESTADO_RECHAZADA, 'Rechazada'),
        (ESTADO_ANULADA, 'Anulada'),
    ]

    TIPO_NUEVA = 'NUEVA'
    TIPO_RENOVACION = 'RENOVACION'
    TIPOS = [
        (TIPO_NUEVA, 'Primera matrícula'),
        (TIPO_RENOVACION, 'Renovación'),
    ]

    # Datos principales
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código de matrícula')
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='matriculas')
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE, related_name='matriculas')
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='matriculas_solicitadas')
    tipo = models.CharField(max_length=15, choices=TIPOS, default=TIPO_NUEVA)
    estado = models.CharField(max_length=15, choices=ESTADOS, default=ESTADO_PENDIENTE)

    # Seguimiento
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    revisado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matriculas_revisadas'
    )
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    motivo_rechazo = models.TextField(blank=True, verbose_name='Motivo de rechazo')

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.codigo} - {self.estudiante}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            from apps.core.utils import generar_codigo_matricula
            self.codigo = generar_codigo_matricula()
        super().save(*args, **kwargs)


class HistorialMatricula(models.Model):
    """Registro de cambios de estado en la matrícula"""
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=15)
    estado_nuevo = models.CharField(max_length=15)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.matricula.codigo}: {self.estado_anterior} → {self.estado_nuevo}"
"@

New-File "$BASE_PATH\apps\matriculas\admin.py" @"
from django.contrib import admin
from .models import Matricula, HistorialMatricula


class HistorialInline(admin.TabularInline):
    model = HistorialMatricula
    extra = 0
    readonly_fields = ['estado_anterior', 'estado_nuevo', 'usuario', 'fecha']


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'estudiante', 'paralelo', 'tipo', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'tipo', 'paralelo__periodo']
    search_fields = ['codigo', 'estudiante__nombres', 'estudiante__apellidos', 'estudiante__cedula']
    inlines = [HistorialInline]
    readonly_fields = ['codigo', 'fecha_solicitud']
"@

New-File "$BASE_PATH\apps\matriculas\views.py" @"
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Matricula


@login_required
def dashboard(request):
    """Panel principal según el rol del usuario"""
    if request.user.es_secretaria:
        pendientes = Matricula.objects.filter(estado=Matricula.ESTADO_PENDIENTE).count()
        en_revision = Matricula.objects.filter(estado=Matricula.ESTADO_EN_REVISION).count()
        aprobadas = Matricula.objects.filter(estado=Matricula.ESTADO_APROBADA).count()
        context = {
            'pendientes': pendientes,
            'en_revision': en_revision,
            'aprobadas': aprobadas,
            'ultimas_solicitudes': Matricula.objects.filter(estado=Matricula.ESTADO_PENDIENTE)[:10],
        }
    else:
        mis_matriculas = Matricula.objects.filter(solicitante=request.user)
        context = {'mis_matriculas': mis_matriculas}
    return render(request, 'matriculas/dashboard.html', context)


@login_required
def lista_matriculas(request):
    if request.user.es_secretaria:
        matriculas = Matricula.objects.all().select_related('estudiante', 'paralelo', 'solicitante')
    else:
        matriculas = Matricula.objects.filter(solicitante=request.user)

    estado = request.GET.get('estado')
    if estado:
        matriculas = matriculas.filter(estado=estado)

    return render(request, 'matriculas/lista.html', {
        'matriculas': matriculas,
        'estados': Matricula.ESTADOS,
    })


@login_required
def detalle_matricula(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    return render(request, 'matriculas/detalle.html', {'matricula': matricula})
"@

New-File "$BASE_PATH\apps\matriculas\urls.py" @"
from django.urls import path
from . import views

app_name = 'matriculas'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('lista/', views.lista_matriculas, name='lista'),
    path('<int:pk>/', views.detalle_matricula, name='detalle'),
]
"@

New-File "$BASE_PATH\apps\matriculas\apps.py" @"
from django.apps import AppConfig

class MatriculasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.matriculas'
    verbose_name = 'Matrículas'
"@

Write-Host "   OK - Módulos estudiantes, periodos, matriculas creados" -ForegroundColor Green

# ─────────────────────────────────────────
# MÓDULOS: documentos, notificaciones, reportes
# ─────────────────────────────────────────
Write-Host "[7/9] Creando módulos documentos, notificaciones y reportes..." -ForegroundColor Yellow

# ─── documentos ───
New-File "$BASE_PATH\apps\documentos\__init__.py" ""
New-File "$BASE_PATH\apps\documentos\migrations\__init__.py" ""

New-File "$BASE_PATH\apps\documentos\models.py" @"
"""
Gestión de documentos requeridos para la matrícula
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.matriculas.models import Matricula


class TipoDocumento(TimeStampedModel):
    """Catálogo de tipos de documentos requeridos"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre del documento')
    descripcion = models.TextField(blank=True, verbose_name='Descripción/Instrucciones')
    es_obligatorio = models.BooleanField(default=True, verbose_name='Es obligatorio')
    aplica_primera_vez = models.BooleanField(default=True, verbose_name='Aplica para primera matrícula')
    aplica_renovacion = models.BooleanField(default=False, verbose_name='Aplica para renovación')
    aplica_discapacidad = models.BooleanField(default=False, verbose_name='Aplica para discapacidad')
    formatos_permitidos = models.CharField(max_length=100, default='PDF,JPG,PNG', verbose_name='Formatos permitidos')

    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class DocumentoMatricula(TimeStampedModel):
    """Documento subido para una matrícula específica"""
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_VERIFICADO = 'VERIFICADO'
    ESTADO_RECHAZADO = 'RECHAZADO'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente de verificación'),
        (ESTADO_VERIFICADO, 'Verificado'),
        (ESTADO_RECHAZADO, 'Rechazado'),
    ]

    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='documentos/matriculas/%Y/%m/', verbose_name='Archivo')
    estado = models.CharField(max_length=15, choices=ESTADOS, default=ESTADO_PENDIENTE)
    observacion = models.TextField(blank=True, verbose_name='Observación del revisor')
    verificado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_verificados'
    )

    class Meta:
        verbose_name = 'Documento de Matrícula'
        verbose_name_plural = 'Documentos de Matrícula'

    def __str__(self):
        return f"{self.tipo} - {self.matricula.codigo}"
"@

New-File "$BASE_PATH\apps\documentos\admin.py" @"
from django.contrib import admin
from .models import TipoDocumento, DocumentoMatricula


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'es_obligatorio', 'aplica_primera_vez', 'aplica_renovacion', 'is_active']
    list_filter = ['es_obligatorio', 'aplica_primera_vez']


@admin.register(DocumentoMatricula)
class DocumentoMatriculaAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'estado', 'verificado_por', 'updated_at']
    list_filter = ['estado']
"@

New-File "$BASE_PATH\apps\documentos\views.py" @"
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DocumentoMatricula


@login_required
def lista_documentos_matricula(request, matricula_pk):
    from apps.matriculas.models import Matricula
    matricula = get_object_or_404(Matricula, pk=matricula_pk)
    documentos = DocumentoMatricula.objects.filter(matricula=matricula)
    return render(request, 'documentos/lista.html', {
        'matricula': matricula,
        'documentos': documentos
    })
"@

New-File "$BASE_PATH\apps\documentos\urls.py" @"
from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    path('matricula/<int:matricula_pk>/', views.lista_documentos_matricula, name='lista'),
]
"@

New-File "$BASE_PATH\apps\documentos\apps.py" @"
from django.apps import AppConfig

class DocumentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.documentos'
    verbose_name = 'Documentos'
"@

# ─── notificaciones ───
New-File "$BASE_PATH\apps\notificaciones\__init__.py" ""
New-File "$BASE_PATH\apps\notificaciones\migrations\__init__.py" ""

New-File "$BASE_PATH\apps\notificaciones\models.py" @"
"""
Notificaciones internas del sistema
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.usuarios.models import Usuario


class Notificacion(TimeStampedModel):
    TIPO_INFO = 'INFO'
    TIPO_EXITO = 'EXITO'
    TIPO_ADVERTENCIA = 'ADVERTENCIA'
    TIPO_ERROR = 'ERROR'

    TIPOS = [
        (TIPO_INFO, 'Información'),
        (TIPO_EXITO, 'Éxito'),
        (TIPO_ADVERTENCIA, 'Advertencia'),
        (TIPO_ERROR, 'Error'),
    ]

    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=15, choices=TIPOS, default=TIPO_INFO)
    titulo = models.CharField(max_length=200, verbose_name='Título')
    mensaje = models.TextField(verbose_name='Mensaje')
    leida = models.BooleanField(default=False, verbose_name='Leída')
    url_accion = models.CharField(max_length=200, blank=True, verbose_name='URL de acción')

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} → {self.destinatario}"
"@

New-File "$BASE_PATH\apps\notificaciones\services.py" @"
"""
Servicio de notificaciones: email + notificaciones internas
"""
from .models import Notificacion
from apps.core.utils import enviar_email_sistema


def notificar_solicitud_recibida(matricula):
    """Notifica al representante que su solicitud fue recibida"""
    Notificacion.objects.create(
        destinatario=matricula.solicitante,
        tipo=Notificacion.TIPO_INFO,
        titulo='Solicitud de matrícula recibida',
        mensaje=f'Su solicitud de matrícula para {matricula.estudiante.nombre_completo} '
                f'ha sido recibida. Código: {matricula.codigo}',
        url_accion=f'/matriculas/{matricula.pk}/'
    )
    enviar_email_sistema(
        destinatario=matricula.solicitante.email,
        asunto=f'[SFQ] Solicitud recibida - {matricula.codigo}',
        mensaje=f'Su solicitud de matrícula ha sido registrada exitosamente.\n'
                f'Código: {matricula.codigo}\n'
                f'Estado: Pendiente de revisión\n\n'
                f'Le notificaremos cuando haya novedades.'
    )


def notificar_matricula_aprobada(matricula):
    """Notifica al representante que la matrícula fue aprobada"""
    Notificacion.objects.create(
        destinatario=matricula.solicitante,
        tipo=Notificacion.TIPO_EXITO,
        titulo='¡Matrícula aprobada!',
        mensaje=f'La matrícula de {matricula.estudiante.nombre_completo} '
                f'ha sido APROBADA. Puede descargar el certificado.',
        url_accion=f'/matriculas/{matricula.pk}/'
    )
    enviar_email_sistema(
        destinatario=matricula.solicitante.email,
        asunto=f'[SFQ] Matrícula aprobada - {matricula.codigo}',
        mensaje=f'¡Felicitaciones! La matrícula de {matricula.estudiante.nombre_completo} '
                f'ha sido aprobada.\n\nIngrese al sistema para descargar el certificado.'
    )


def notificar_matricula_rechazada(matricula):
    """Notifica al representante que la matrícula fue rechazada"""
    Notificacion.objects.create(
        destinatario=matricula.solicitante,
        tipo=Notificacion.TIPO_ADVERTENCIA,
        titulo='Matrícula requiere correcciones',
        mensaje=f'Su solicitud requiere correcciones. Motivo: {matricula.motivo_rechazo}',
        url_accion=f'/matriculas/{matricula.pk}/'
    )
"@

New-File "$BASE_PATH\apps\notificaciones\views.py" @"
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notificacion


@login_required
def lista_notificaciones(request):
    notificaciones = Notificacion.objects.filter(destinatario=request.user)
    # Marcar como leídas
    notificaciones.filter(leida=False).update(leida=True)
    return render(request, 'notificaciones/lista.html', {'notificaciones': notificaciones})
"@

New-File "$BASE_PATH\apps\notificaciones\urls.py" @"
from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.lista_notificaciones, name='lista'),
]
"@

New-File "$BASE_PATH\apps\notificaciones\admin.py" @"
from django.contrib import admin
from .models import Notificacion

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'destinatario', 'tipo', 'leida', 'created_at']
    list_filter = ['tipo', 'leida']
"@

New-File "$BASE_PATH\apps\notificaciones\apps.py" @"
from django.apps import AppConfig

class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notificaciones'
    verbose_name = 'Notificaciones'
"@

# ─── reportes ───
New-File "$BASE_PATH\apps\reportes\__init__.py" ""
New-File "$BASE_PATH\apps\reportes\migrations\__init__.py" ""

New-File "$BASE_PATH\apps\reportes\views.py" @"
"""
Reportes, estadísticas y exportación de datos
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.matriculas.models import Matricula
from apps.periodos.models import PeriodoAcademico, Paralelo


@login_required
def dashboard_reportes(request):
    """Panel de reportes y estadísticas"""
    periodo_activo = PeriodoAcademico.objects.filter(es_activo=True).first()

    stats = {}
    if periodo_activo:
        matriculas = Matricula.objects.filter(paralelo__periodo=periodo_activo)
        stats = {
            'total': matriculas.count(),
            'aprobadas': matriculas.filter(estado=Matricula.ESTADO_APROBADA).count(),
            'pendientes': matriculas.filter(estado=Matricula.ESTADO_PENDIENTE).count(),
            'rechazadas': matriculas.filter(estado=Matricula.ESTADO_RECHAZADA).count(),
        }

    return render(request, 'reportes/dashboard.html', {
        'periodo': periodo_activo,
        'stats': stats,
    })


@login_required
def reporte_matriculados(request):
    """Listado de matriculados por nivel y paralelo"""
    periodo_activo = PeriodoAcademico.objects.filter(es_activo=True).first()
    paralelos = Paralelo.objects.filter(
        periodo=periodo_activo,
        is_active=True
    ).prefetch_related('matriculas__estudiante') if periodo_activo else []

    return render(request, 'reportes/matriculados.html', {
        'periodo': periodo_activo,
        'paralelos': paralelos,
    })
"@

New-File "$BASE_PATH\apps\reportes\urls.py" @"
from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard'),
    path('matriculados/', views.reporte_matriculados, name='matriculados'),
]
"@

New-File "$BASE_PATH\apps\reportes\admin.py" "from django.contrib import admin"

New-File "$BASE_PATH\apps\reportes\apps.py" @"
from django.apps import AppConfig

class ReportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reportes'
    verbose_name = 'Reportes'
"@

Write-Host "   OK - Módulos documentos, notificaciones, reportes creados" -ForegroundColor Green

# ─────────────────────────────────────────
# TEMPLATES BASE
# ─────────────────────────────────────────
Write-Host "[8/9] Creando templates base..." -ForegroundColor Yellow

New-File "$BASE_PATH\templates\base.html" @"
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ SCHOOL_NAME }}{% endblock %}</title>
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold" href="{% url 'core:home' %}">
                <i class="bi bi-mortarboard-fill me-2"></i>{{ SCHOOL_NAME }}
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMain">
                {% if user.is_authenticated %}
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'matriculas:dashboard' %}"><i class="bi bi-grid me-1"></i>Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'matriculas:lista' %}"><i class="bi bi-list-check me-1"></i>Matrículas</a>
                    </li>
                    {% if user.es_secretaria %}
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'estudiantes:lista' %}"><i class="bi bi-people me-1"></i>Estudiantes</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'reportes:dashboard' %}"><i class="bi bi-bar-chart me-1"></i>Reportes</a>
                    </li>
                    {% endif %}
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'notificaciones:lista' %}">
                            <i class="bi bi-bell"></i>
                        </a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            <i class="bi bi-person-circle me-1"></i>{{ user.get_full_name|default:user.username }}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="{% url 'usuarios:perfil' %}"><i class="bi bi-person me-2"></i>Mi Perfil</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="{% url 'usuarios:logout' %}"><i class="bi bi-box-arrow-right me-2"></i>Cerrar Sesión</a></li>
                        </ul>
                    </li>
                </ul>
                {% endif %}
            </div>
        </div>
    </nav>

    <!-- Mensajes del sistema -->
    <div class="container-fluid mt-2">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>

    <!-- Contenido principal -->
    <main class="container-fluid py-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="footer mt-auto py-3 bg-light border-top">
        <div class="container text-center">
            <small class="text-muted">
                {{ SCHOOL_NAME }} · {{ SCHOOL_CITY }}, {{ SCHOOL_PROVINCE }} · AMIE: {{ SCHOOL_AMIE }}
            </small>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"@

New-File "$BASE_PATH\templates\core\home.html" @"
{% extends 'base.html' %}
{% block title %}Inicio - {{ SCHOOL_NAME }}{% endblock %}
{% block content %}
<div class="row">
    <div class="col-12">
        <h2><i class="bi bi-house me-2"></i>Bienvenido al Sistema de Matrículas</h2>
        <p class="text-muted">{{ SCHOOL_NAME }}</p>
    </div>
</div>
{% endblock %}
"@

New-File "$BASE_PATH\templates\usuarios\login.html" @"
{% extends 'base.html' %}
{% load crispy_forms_tags %}
{% block title %}Iniciar Sesión - {{ SCHOOL_NAME }}{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-5">
        <div class="card shadow">
            <div class="card-header bg-primary text-white text-center py-4">
                <h4 class="mb-0"><i class="bi bi-mortarboard-fill me-2"></i>{{ SCHOOL_NAME }}</h4>
                <small>Sistema de Matrículas en Línea</small>
            </div>
            <div class="card-body p-4">
                <h5 class="card-title mb-4">Iniciar Sesión</h5>
                <form method="post">
                    {% csrf_token %}
                    {{ form|crispy }}
                    <div class="d-grid mt-3">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="bi bi-box-arrow-in-right me-2"></i>Ingresar
                        </button>
                    </div>
                </form>
                <hr>
                <div class="text-center">
                    <p class="mb-0">¿No tiene cuenta?
                        <a href="{% url 'usuarios:registro' %}">Regístrese aquí</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"@

New-File "$BASE_PATH\templates\matriculas\dashboard.html" @"
{% extends 'base.html' %}
{% block title %}Dashboard - {{ SCHOOL_NAME }}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2><i class="bi bi-grid me-2"></i>Panel Principal</h2>
</div>

{% if user.es_secretaria %}
<!-- Dashboard Secretaria/Admin -->
<div class="row g-3 mb-4">
    <div class="col-md-3">
        <div class="card border-warning">
            <div class="card-body text-center">
                <h3 class="text-warning">{{ pendientes }}</h3>
                <p class="mb-0">Pendientes</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card border-info">
            <div class="card-body text-center">
                <h3 class="text-info">{{ en_revision }}</h3>
                <p class="mb-0">En Revisión</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card border-success">
            <div class="card-body text-center">
                <h3 class="text-success">{{ aprobadas }}</h3>
                <p class="mb-0">Aprobadas</p>
            </div>
        </div>
    </div>
</div>
{% else %}
<!-- Dashboard Representante -->
<div class="row">
    <div class="col-12">
        <h5>Mis Solicitudes de Matrícula</h5>
        {% for matricula in mis_matriculas %}
        <div class="card mb-2">
            <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                    <strong>{{ matricula.estudiante }}</strong><br>
                    <small class="text-muted">{{ matricula.codigo }}</small>
                </div>
                <span class="badge bg-{% if matricula.estado == 'APROBADA' %}success{% elif matricula.estado == 'RECHAZADA' %}danger{% else %}warning text-dark{% endif %}">
                    {{ matricula.get_estado_display }}
                </span>
            </div>
        </div>
        {% empty %}
        <p class="text-muted">No tiene solicitudes registradas.</p>
        {% endfor %}
    </div>
</div>
{% endif %}
{% endblock %}
"@

# CSS base
New-File "$BASE_PATH\static\css\main.css" @"
/* ─────────────────────────────────────
   SFQ MATRICULAS - Estilos principales
   ───────────────────────────────────── */

body {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.navbar-brand {
    font-size: 1rem;
}

.card {
    border-radius: 0.5rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,.075);
}

.footer {
    font-size: 0.85rem;
}

/* Tabla responsive */
.table-hover tbody tr:hover {
    background-color: rgba(13, 110, 253, 0.05);
}

/* Badges de estado */
.badge-pendiente { background-color: #ffc107; color: #000; }
.badge-aprobada  { background-color: #198754; }
.badge-rechazada { background-color: #dc3545; }
"@

Write-Host "   OK - Templates y assets creados" -ForegroundColor Green

# ─────────────────────────────────────────
# ARCHIVOS UTILITARIOS FINALES
# ─────────────────────────────────────────
Write-Host "[9/9] Creando archivos utilitarios finales..." -ForegroundColor Yellow

# Makefile para comandos frecuentes
New-File "$BASE_PATH\Makefile" @"
# ─────────────────────────────────────────
#  COMANDOS DE DESARROLLO - SFQ MATRICULAS
#  Usar con: make <comando>
# ─────────────────────────────────────────

.PHONY: build up down restart logs shell migrate makemigrations collectstatic createsuperuser

# Construir e iniciar contenedores
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart web

# Ver logs
logs:
	docker-compose logs -f web

# Entrar al contenedor
shell:
	docker-compose exec web python manage.py shell

# Base de datos
migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

# Archivos estáticos
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Crear superusuario
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Cargar datos iniciales
loaddata:
	docker-compose exec web python manage.py loaddata fixtures/initial_data.json
"@

# README
New-File "$BASE_PATH\README.md" @"
# Sistema de Matrículas en Línea
## Escuela Fiscomisional San Francisco de Quito

### Stack Tecnológico
- **Backend:** Django 4.2
- **Base de datos:** PostgreSQL 15
- **Contenedores:** Docker + Docker Compose
- **Frontend:** Bootstrap 5

### Módulos del sistema
| Módulo | Descripción |
|--------|-------------|
| `core` | Base compartida y utilidades |
| `usuarios` | Autenticación y roles |
| `estudiantes` | Ficha del estudiante |
| `periodos` | Años lectivos y paralelos |
| `matriculas` | Flujo principal de matrícula |
| `documentos` | Gestión de requisitos documentales |
| `notificaciones` | Comunicación con representantes |
| `reportes` | Estadísticas y exportación |

### Inicio rápido

```bash
# 1. Clonar y configurar
cp .env.example .env
# Editar .env con tus datos

# 2. Construir e iniciar
docker-compose build
docker-compose up -d

# 3. Migrar base de datos
docker-compose exec web python manage.py migrate

# 4. Crear superusuario
docker-compose exec web python manage.py createsuperuser

# 5. Acceder
# http://localhost:8000
# http://localhost:8000/admin
```

### Roles del sistema
- **Administrador:** Acceso total al sistema
- **Secretaria:** Gestión de matrículas y documentos
- **Representante:** Portal de solicitud de matrícula
- **Docente:** Consulta de listas de estudiantes
"@

# Script CMD de inicio rápido para Windows
New-File "$BASE_PATH\iniciar.bat" @"
@echo off
echo ========================================
echo  SFQ MATRICULAS - Inicio rapido
echo ========================================
echo.

IF NOT EXIST .env (
    echo [!] Copiando .env de ejemplo...
    copy .env.example .env
    echo [!] Por favor edita el archivo .env antes de continuar
    pause
    exit
)

echo [1] Construyendo contenedores...
docker-compose build

echo [2] Iniciando servicios...
docker-compose up -d

echo [3] Esperando a que la DB este lista...
timeout /t 8 /nobreak > NUL

echo [4] Aplicando migraciones...
docker-compose exec web python manage.py migrate

echo.
echo ========================================
echo  SISTEMA LISTO
echo  URL: http://localhost:8000
echo  Admin: http://localhost:8000/admin
echo ========================================
echo.
pause
"@

Write-Host "   OK - Archivos utilitarios creados" -ForegroundColor Green

# ─────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────
Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "   ESTRUCTURA CREADA EXITOSAMENTE" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Ubicación: $BASE_PATH (carpeta actual)" -ForegroundColor White
Write-Host ""
Write-Host "  Módulos creados:" -ForegroundColor Cyan
Write-Host "   apps/core              - Base compartida"
Write-Host "   apps/usuarios          - Autenticación y roles"
Write-Host "   apps/estudiantes       - Ficha del estudiante"
Write-Host "   apps/periodos          - Años lectivos y paralelos"
Write-Host "   apps/matriculas        - Flujo principal"
Write-Host "   apps/documentos        - Requisitos documentales"
Write-Host "   apps/notificaciones    - Comunicación"
Write-Host "   apps/reportes          - Estadísticas"
Write-Host ""
Write-Host "  Siguiente paso:" -ForegroundColor Yellow
Write-Host "   1. Editar el archivo .env con tus datos"
Write-Host "   2. Ejecutar: .\iniciar.bat"
Write-Host "      o manualmente: docker-compose up --build"
Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
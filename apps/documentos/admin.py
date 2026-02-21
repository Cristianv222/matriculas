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

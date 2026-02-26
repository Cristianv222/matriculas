"""
============================================================
  VISTAS: apps.documentos
  Subida, verificación y gestión de documentos por matrícula
============================================================
"""
import os
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, TemplateView

from .models import DocumentoMatricula, TipoDocumento
from apps.matriculas.models import Matricula


# ─────────────────────────────────────────────────────────────────────────────
#  Mixins
# ─────────────────────────────────────────────────────────────────────────────

class PersonalMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        if not u.is_authenticated:
            return False
        if u.is_staff or u.is_superuser:
            return True
        return getattr(u, 'rol', '') in ('ADMIN', 'SECRETARIA')


def _puede_ver_matricula(user, matricula):
    """Verifica si el usuario puede acceder a una matrícula."""
    if user.is_staff or user.is_superuser:
        return True
    if getattr(user, 'rol', '') in ('ADMIN', 'SECRETARIA'):
        return True
    return matricula.solicitante == user


# ─────────────────────────────────────────────────────────────────────────────
#  LISTA DE DOCUMENTOS POR MATRÍCULA
# ─────────────────────────────────────────────────────────────────────────────

class DocumentosMatriculaView(LoginRequiredMixin, View):
    """
    Lista todos los documentos de una matrícula.
    Muestra qué falta, qué está pendiente y qué está verificado.
    """
    template_name = 'documentos/lista.html'

    def get(self, request, matricula_pk):
        matricula = get_object_or_404(Matricula, pk=matricula_pk)

        if not _puede_ver_matricula(request.user, matricula):
            raise PermissionDenied

        # Documentos ya subidos
        documentos = DocumentoMatricula.objects.filter(
            matricula=matricula
        ).select_related('tipo', 'verificado_por')

        # Tipos requeridos para esta matrícula
        tipos_requeridos = [
            t for t in TipoDocumento.objects.filter(is_active=True).order_by('orden')
            if t.aplica_para_matricula(matricula)
        ]

        # Mapa tipo_id → documento subido
        docs_map = {d.tipo_id: d for d in documentos}

        # Lista combinada: requisito + estado actual
        requisitos = []
        for tipo in tipos_requeridos:
            requisitos.append({
                'tipo': tipo,
                'documento': docs_map.get(tipo.pk),
            })

        # Contadores
        total       = len(tipos_requeridos)
        verificados = sum(1 for r in requisitos if r['documento'] and r['documento'].estado == DocumentoMatricula.ESTADO_VERIFICADO)
        pendientes  = sum(1 for r in requisitos if r['documento'] and r['documento'].estado == DocumentoMatricula.ESTADO_PENDIENTE)
        rechazados  = sum(1 for r in requisitos if r['documento'] and r['documento'].estado == DocumentoMatricula.ESTADO_RECHAZADO)
        faltantes   = sum(1 for r in requisitos if not r['documento'])

        es_personal = request.user.is_staff or request.user.is_superuser or \
                      getattr(request.user, 'rol', '') in ('ADMIN', 'SECRETARIA')

        return render(request, self.template_name, {
            'matricula':   matricula,
            'requisitos':  requisitos,
            'total':       total,
            'verificados': verificados,
            'pendientes':  pendientes,
            'rechazados':  rechazados,
            'faltantes':   faltantes,
            'es_personal': es_personal,
        })


# ─────────────────────────────────────────────────────────────────────────────
#  SUBIR DOCUMENTO
# ─────────────────────────────────────────────────────────────────────────────

class SubirDocumentoView(LoginRequiredMixin, View):
    """El representante sube un documento para una matrícula."""
    template_name = 'documentos/subir.html'

    def _get_matricula_y_tipo(self, matricula_pk, tipo_pk, user):
        matricula = get_object_or_404(Matricula, pk=matricula_pk)
        tipo      = get_object_or_404(TipoDocumento, pk=tipo_pk)
        if not _puede_ver_matricula(user, matricula):
            raise PermissionDenied
        return matricula, tipo

    def get(self, request, matricula_pk, tipo_pk):
        matricula, tipo = self._get_matricula_y_tipo(matricula_pk, tipo_pk, request.user)
        # Si ya existe, pre-cargar
        documento = DocumentoMatricula.objects.filter(
            matricula=matricula, tipo=tipo
        ).first()
        return render(request, self.template_name, {
            'matricula': matricula,
            'tipo':      tipo,
            'documento': documento,
        })

    def post(self, request, matricula_pk, tipo_pk):
        matricula, tipo = self._get_matricula_y_tipo(matricula_pk, tipo_pk, request.user)
        archivo = request.FILES.get('archivo')

        if not archivo:
            messages.error(request, 'Debe seleccionar un archivo.')
            return redirect(request.path)

        # Validar extensión
        ext = os.path.splitext(archivo.name)[1].lower().lstrip('.')
        if ext not in tipo.extensiones_lista:
            messages.error(request,
                f'Formato no permitido. Se aceptan: {tipo.formatos_permitidos}')
            return redirect(request.path)

        # Validar tamaño
        limite = tipo.tamano_maximo_mb * 1024 * 1024
        if archivo.size > limite:
            messages.error(request,
                f'El archivo supera el límite de {tipo.tamano_maximo_mb} MB.')
            return redirect(request.path)

        # Crear o reemplazar
        doc, created = DocumentoMatricula.objects.get_or_create(
            matricula=matricula,
            tipo=tipo,
            defaults={
                'archivo': archivo,
                'nombre_original': archivo.name,
                'tamano_bytes': archivo.size,
                'estado': DocumentoMatricula.ESTADO_PENDIENTE,
            }
        )
        if not created:
            # Eliminar archivo anterior y reemplazar
            if doc.archivo:
                try:
                    os.remove(doc.archivo.path)
                except Exception:
                    pass
            doc.archivo         = archivo
            doc.nombre_original = archivo.name
            doc.tamano_bytes    = archivo.size
            doc.estado          = DocumentoMatricula.ESTADO_PENDIENTE
            doc.observacion     = ''
            doc.verificado_por  = None
            doc.fecha_verificacion = None
            doc.save()

        messages.success(request,
            f'Documento "{tipo.nombre}" subido correctamente. Pendiente de verificación.')
        return redirect('documentos:lista', matricula_pk=matricula.pk)


# ─────────────────────────────────────────────────────────────────────────────
#  DESCARGAR / VER DOCUMENTO
# ─────────────────────────────────────────────────────────────────────────────

class DescargarDocumentoView(LoginRequiredMixin, View):
    """Descarga o visualiza un documento."""

    def get(self, request, pk):
        doc = get_object_or_404(DocumentoMatricula, pk=pk)
        if not _puede_ver_matricula(request.user, doc.matricula):
            raise PermissionDenied
        if not doc.archivo:
            raise Http404('El archivo no existe.')
        try:
            response = FileResponse(
                open(doc.archivo.path, 'rb'),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = (
                f'inline; filename="{doc.nombre_original or doc.archivo.name}"'
            )
            return response
        except FileNotFoundError:
            raise Http404('El archivo no se encontró en el servidor.')


# ─────────────────────────────────────────────────────────────────────────────
#  ELIMINAR DOCUMENTO (representante, solo si está rechazado o pendiente)
# ─────────────────────────────────────────────────────────────────────────────

class EliminarDocumentoView(LoginRequiredMixin, View):

    def post(self, request, pk):
        doc = get_object_or_404(DocumentoMatricula, pk=pk)
        matricula_pk = doc.matricula_id

        # Solo el solicitante o staff puede eliminar
        if not _puede_ver_matricula(request.user, doc.matricula):
            raise PermissionDenied

        # Representante solo puede eliminar si no está verificado
        if not (request.user.is_staff or request.user.is_superuser):
            if doc.estado == DocumentoMatricula.ESTADO_VERIFICADO:
                messages.error(request,
                    'No puede eliminar un documento ya verificado.')
                return redirect('documentos:lista', matricula_pk=matricula_pk)

        nombre = doc.tipo.nombre
        if doc.archivo:
            try:
                os.remove(doc.archivo.path)
            except Exception:
                pass
        doc.delete()
        messages.warning(request, f'Documento "{nombre}" eliminado.')
        return redirect('documentos:lista', matricula_pk=matricula_pk)


# ─────────────────────────────────────────────────────────────────────────────
#  VERIFICAR DOCUMENTO (secretaría)
# ─────────────────────────────────────────────────────────────────────────────

class VerificarDocumentoView(PersonalMixin, View):
    """Secretaría marca un documento como verificado."""

    def post(self, request, pk):
        doc = get_object_or_404(DocumentoMatricula, pk=pk)
        doc.verificar(request.user)
        messages.success(request,
            f'Documento "{doc.tipo.nombre}" verificado correctamente.')
        return redirect('documentos:lista', matricula_pk=doc.matricula_id)


# ─────────────────────────────────────────────────────────────────────────────
#  RECHAZAR DOCUMENTO (secretaría)
# ─────────────────────────────────────────────────────────────────────────────

class RechazarDocumentoView(PersonalMixin, View):
    """Secretaría rechaza un documento indicando el motivo."""

    def post(self, request, pk):
        doc        = get_object_or_404(DocumentoMatricula, pk=pk)
        observacion = request.POST.get('observacion', '').strip()
        if not observacion:
            messages.error(request, 'Debe indicar el motivo del rechazo.')
            return redirect('documentos:lista', matricula_pk=doc.matricula_id)
        try:
            doc.rechazar(request.user, observacion)
            messages.warning(request,
                f'Documento "{doc.tipo.nombre}" rechazado. El representante será notificado.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('documentos:lista', matricula_pk=doc.matricula_id)


# ─────────────────────────────────────────────────────────────────────────────
#  PANEL DE DOCUMENTOS (secretaría) — todos los documentos pendientes
# ─────────────────────────────────────────────────────────────────────────────

class PanelDocumentosView(PersonalMixin, ListView):
    """Panel para secretaría: todos los documentos pendientes de revisión."""
    model               = DocumentoMatricula
    template_name       = 'documentos/panel.html'
    context_object_name = 'documentos'
    paginate_by         = 20

    def get_queryset(self):
        qs = DocumentoMatricula.objects.select_related(
            'matricula', 'matricula__estudiante',
            'tipo', 'verificado_por'
        )
        estado = self.request.GET.get('estado', DocumentoMatricula.ESTADO_PENDIENTE)
        if estado:
            qs = qs.filter(estado=estado)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estados']         = DocumentoMatricula.ESTADOS
        ctx['estado_filtrado'] = self.request.GET.get('estado', DocumentoMatricula.ESTADO_PENDIENTE)
        ctx['conteo'] = {
            'pendientes':  DocumentoMatricula.objects.filter(estado=DocumentoMatricula.ESTADO_PENDIENTE).count(),
            'verificados': DocumentoMatricula.objects.filter(estado=DocumentoMatricula.ESTADO_VERIFICADO).count(),
            'rechazados':  DocumentoMatricula.objects.filter(estado=DocumentoMatricula.ESTADO_RECHAZADO).count(),
        }
        return ctx
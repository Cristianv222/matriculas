"""
============================================================
  VISTAS: apps.matriculas
  Cubre los flujos de Representante, Secretaría y Admin.
============================================================
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView, DetailView, ListView,
    TemplateView, UpdateView,
)

from .models import Matricula, HistorialMatricula


# ─────────────────────────────────────────────────────────────────────────────
#  Mixins de permisos reutilizables
# ─────────────────────────────────────────────────────────────────────────────

class RepresentanteMixin(LoginRequiredMixin):
    """Solo el propio solicitante (representante) accede."""

    def get_queryset(self):
        return Matricula.objects.filter(solicitante=self.request.user)


class PersonalMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Secretaría, coordinadores y staff del sistema."""

    def test_func(self):
        return self.request.user.is_staff


class AdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Solo administradores / superusuarios."""

    def test_func(self):
        return self.request.user.is_superuser


# ─────────────────────────────────────────────────────────────────────────────
#  REPRESENTANTE / SOLICITANTE
# ─────────────────────────────────────────────────────────────────────────────

class MatriculaListView(RepresentanteMixin, ListView):
    """Lista las matrículas del representante autenticado."""
    model               = Matricula
    template_name       = 'matriculas/lista.html'
    context_object_name = 'matriculas'
    paginate_by         = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'estudiante', 'paralelo', 'paralelo__periodo'
        )
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estados']         = Matricula.ESTADOS
        ctx['estado_filtrado'] = self.request.GET.get('estado', '')
        return ctx


class MatriculaCreateView(RepresentanteMixin, CreateView):
    """El representante crea una nueva solicitud de matrícula."""
    model         = Matricula
    template_name = 'matriculas/formulario.html'
    fields        = ['estudiante', 'paralelo', 'tipo', 'matricula_anterior']

    def get_success_url(self):
        return reverse_lazy('matriculas:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.solicitante = self.request.user
        try:
            form.instance.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        messages.success(self.request,
            f'Solicitud de matrícula {form.instance.codigo} enviada correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nueva solicitud de matrícula'
        ctx['accion'] = 'Enviar solicitud'
        return ctx


class MatriculaDetailView(RepresentanteMixin, DetailView):
    """Detalle de la matrícula visible al representante."""
    model         = Matricula
    template_name = 'matriculas/detalle.html'

    def get_queryset(self):
        # Representantes solo ven las suyas; el staff ve todas.
        if self.request.user.is_staff:
            return Matricula.objects.all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['historial'] = self.object.historial.select_related('usuario').order_by('fecha')
        return ctx


class MatriculaUpdateView(RepresentanteMixin, UpdateView):
    """El representante edita una matrícula en estado editable."""
    model         = Matricula
    template_name = 'matriculas/formulario.html'
    fields        = ['estudiante', 'paralelo', 'tipo', 'matricula_anterior']

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.es_editable:
            messages.error(self.request, 'Esta matrícula no puede editarse en su estado actual.')
            raise PermissionError('No editable')
        return obj

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError:
            return redirect('matriculas:lista')

    def get_success_url(self):
        return reverse_lazy('matriculas:detalle', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar solicitud de matrícula'
        ctx['accion'] = 'Guardar cambios'
        return ctx


class MatriculaReenviarView(LoginRequiredMixin, View):
    """El representante reenvía una solicitud rechazada."""

    def post(self, request, pk):
        matricula = get_object_or_404(Matricula, pk=pk, solicitante=request.user)
        try:
            matricula.reenviar(request.user)
            messages.success(request,
                f'La solicitud {matricula.codigo} fue reenviada para revisión.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('matriculas:detalle', pk=pk)


# ─────────────────────────────────────────────────────────────────────────────
#  SECRETARÍA / PERSONAL
# ─────────────────────────────────────────────────────────────────────────────

class PanelSecretariaView(PersonalMixin, ListView):
    """
    Panel de trabajo de la secretaría: todas las matrículas del sistema,
    con filtros por estado, período y búsqueda de estudiante.
    """
    model               = Matricula
    template_name       = 'matriculas/panel_secretaria.html'
    context_object_name = 'matriculas'
    paginate_by         = 20

    def get_queryset(self):
        qs = Matricula.objects.select_related(
            'estudiante', 'paralelo', 'paralelo__periodo',
            'solicitante', 'revisado_por',
        )

        # Filtros desde GET
        estado   = self.request.GET.get('estado')
        periodo  = self.request.GET.get('periodo')
        busqueda = self.request.GET.get('q')

        if estado:
            qs = qs.filter(estado=estado)
        if periodo:
            qs = qs.filter(paralelo__periodo__id=periodo)
        if busqueda:
            qs = qs.filter(
                Q(codigo__icontains=busqueda) |
                Q(estudiante__nombres__icontains=busqueda) |
                Q(estudiante__apellidos__icontains=busqueda) |
                Q(estudiante__numero_identificacion__icontains=busqueda)
            )
        return qs.order_by('-fecha_solicitud')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estados']         = Matricula.ESTADOS
        ctx['estado_filtrado'] = self.request.GET.get('estado', '')
        ctx['busqueda']        = self.request.GET.get('q', '')
        # Contadores rápidos para el dashboard de la secretaría
        ctx['conteo'] = {
            'pendientes':   Matricula.objects.filter(estado=Matricula.ESTADO_PENDIENTE).count(),
            'en_revision':  Matricula.objects.filter(estado=Matricula.ESTADO_EN_REVISION).count(),
            'aprobadas':    Matricula.objects.filter(estado=Matricula.ESTADO_APROBADA).count(),
            'rechazadas':   Matricula.objects.filter(estado=Matricula.ESTADO_RECHAZADA).count(),
        }
        return ctx


class IniciarRevisionView(PersonalMixin, View):
    """Secretaría toma una solicitud para revisarla."""

    def post(self, request, pk):
        matricula = get_object_or_404(Matricula, pk=pk)
        try:
            matricula.iniciar_revision(request.user)
            messages.success(request,
                f'Matrícula {matricula.codigo} en revisión.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('matriculas:detalle', pk=pk)


class AprobarMatriculaView(PersonalMixin, View):
    """Secretaría aprueba una matrícula en revisión."""

    def post(self, request, pk):
        matricula    = get_object_or_404(Matricula, pk=pk)
        observaciones = request.POST.get('observaciones', '')
        try:
            matricula.aprobar(request.user, observaciones)
            messages.success(request,
                f'✅ Matrícula {matricula.codigo} aprobada correctamente.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('matriculas:detalle', pk=pk)


class RechazarMatriculaView(PersonalMixin, View):
    """Secretaría rechaza una matrícula con un motivo."""

    def get(self, request, pk):
        """Muestra el formulario de rechazo."""
        matricula = get_object_or_404(Matricula, pk=pk)
        return _render_modal_o_template(
            request, 'matriculas/rechazar_form.html', {'matricula': matricula}
        )

    def post(self, request, pk):
        matricula = get_object_or_404(Matricula, pk=pk)
        motivo    = request.POST.get('motivo', '').strip()
        if not motivo:
            messages.error(request, 'Debe ingresar el motivo del rechazo.')
            return redirect('matriculas:detalle', pk=pk)
        try:
            matricula.rechazar(request.user, motivo)
            messages.warning(request,
                f'❌ Matrícula {matricula.codigo} rechazada. El representante será notificado.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('matriculas:panel_secretaria')


# ─────────────────────────────────────────────────────────────────────────────
#  ADMINISTRACIÓN
# ─────────────────────────────────────────────────────────────────────────────

class AnularMatriculaView(AdminMixin, View):
    """Solo el administrador puede anular una matrícula aprobada."""

    def get(self, request, pk):
        matricula = get_object_or_404(Matricula, pk=pk)
        return _render_modal_o_template(
            request, 'matriculas/anular_form.html', {'matricula': matricula}
        )

    def post(self, request, pk):
        matricula = get_object_or_404(Matricula, pk=pk)
        motivo    = request.POST.get('motivo', '').strip()
        if not motivo:
            messages.error(request, 'Debe ingresar el motivo de anulación.')
            return redirect('matriculas:detalle', pk=pk)
        try:
            matricula.anular(request.user, motivo)
            messages.warning(request,
                f'🚫 Matrícula {matricula.codigo} anulada.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('matriculas:detalle', pk=pk)


# ─────────────────────────────────────────────────────────────────────────────
#  HISTORIAL
# ─────────────────────────────────────────────────────────────────────────────

class HistorialMatriculaView(PersonalMixin, DetailView):
    """Vista detallada del historial de auditoría de una matrícula."""
    model         = Matricula
    template_name = 'matriculas/historial.html'

    def get_queryset(self):
        return Matricula.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['historial'] = self.object.historial.select_related('usuario').order_by('fecha')
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
#  API JSON
# ─────────────────────────────────────────────────────────────────────────────

class MatriculaEstadoAPIView(LoginRequiredMixin, View):
    """
    Devuelve el estado actual de una matrícula en JSON.
    Útil para actualizar badges en tiempo real vía AJAX.
    """

    def get(self, request, pk):
        matricula = get_object_or_404(Matricula, pk=pk)

        # Representantes solo pueden consultar las suyas
        if not request.user.is_staff and matricula.solicitante != request.user:
            return JsonResponse({'error': 'No autorizado'}, status=403)

        return JsonResponse({
            'pk':              matricula.pk,
            'codigo':          matricula.codigo,
            'estado':          matricula.estado,
            'estado_display':  matricula.get_estado_display(),
            'es_editable':     matricula.es_editable,
            'esta_finalizada': matricula.esta_finalizada,
            'dias_en_proceso': matricula.dias_en_proceso,
            'fecha_solicitud': matricula.fecha_solicitud.isoformat(),
        })


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers internos
# ─────────────────────────────────────────────────────────────────────────────

def _render_modal_o_template(request, template, context):
    """
    Renderiza el template normal.
    Si en el futuro usas django-htmx o similar, aquí puedes
    devolver solo el fragmento de modal.
    """
    from django.shortcuts import render
    return render(request, template, context)
"""
============================================================
  MÓDULO: periodos — views.py
  CBVs web + ViewSets DRF
============================================================
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import PeriodoAcademico, Nivel, Paralelo
from .forms import PeriodoAcademicoForm, NivelForm, ParaleloForm


# ── Mixins de acceso ──────────────────────────────────────────────────────────

class SecretariaRequeridaMixin(UserPassesTestMixin):
    """Permite acceso a secretaria, admin y superusuario."""
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (
            u.is_superuser or getattr(u, 'rol', '') in ['ADMIN', 'SECRETARIA']
        )


class AdminRequeridoMixin(UserPassesTestMixin):
    """Solo admin o superusuario."""
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (
            u.is_superuser or getattr(u, 'rol', '') == 'ADMIN'
        )


# ══════════════════════════════════════════════════════════════════════════════
#  PERÍODO ACADÉMICO
# ══════════════════════════════════════════════════════════════════════════════

class PeriodoListView(LoginRequiredMixin, SecretariaRequeridaMixin, ListView):
    model               = PeriodoAcademico
    template_name       = 'periodos/periodo_lista.html'
    context_object_name = 'periodos'

    def get_queryset(self):
        return super().get_queryset().annotate(
            num_paralelos=Count('paralelos', distinct=True),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['periodo_activo'] = PeriodoAcademico.get_activo()
        return ctx


class PeriodoDetailView(LoginRequiredMixin, SecretariaRequeridaMixin, DetailView):
    model               = PeriodoAcademico
    template_name       = 'periodos/periodo_detalle.html'
    context_object_name = 'periodo'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['paralelos'] = (
            self.object.paralelos
            .select_related('nivel')
            .order_by('nivel__orden', 'nombre')
        )
        return ctx


class PeriodoCreateView(LoginRequiredMixin, AdminRequeridoMixin, CreateView):
    model         = PeriodoAcademico
    form_class    = PeriodoAcademicoForm
    template_name = 'periodos/periodo_formulario.html'
    success_url   = reverse_lazy('periodos:periodo-lista')

    def form_valid(self, form):
        messages.success(self.request, f'Período "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nuevo Período Académico'
        ctx['accion'] = 'Crear período'
        return ctx


class PeriodoUpdateView(LoginRequiredMixin, AdminRequeridoMixin, UpdateView):
    model         = PeriodoAcademico
    form_class    = PeriodoAcademicoForm
    template_name = 'periodos/periodo_formulario.html'
    success_url   = reverse_lazy('periodos:periodo-lista')

    def form_valid(self, form):
        messages.success(self.request, f'Período "{form.instance.nombre}" actualizado.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.nombre}'
        ctx['accion'] = 'Guardar cambios'
        return ctx


# ══════════════════════════════════════════════════════════════════════════════
#  NIVEL
# ══════════════════════════════════════════════════════════════════════════════

class NivelListView(LoginRequiredMixin, SecretariaRequeridaMixin, ListView):
    model               = Nivel
    template_name       = 'periodos/nivel_lista.html'
    context_object_name = 'niveles'


class NivelCreateView(LoginRequiredMixin, AdminRequeridoMixin, CreateView):
    model         = Nivel
    form_class    = NivelForm
    template_name = 'periodos/nivel_formulario.html'
    success_url   = reverse_lazy('periodos:nivel-lista')

    def form_valid(self, form):
        nivel = form.save()
        # Soporte AJAX (modal desde paralelo_formulario)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'id': nivel.pk, 'nombre': nivel.nombre})
        messages.success(self.request, f'Nivel "{nivel.nombre}" creado.')
        return redirect(self.success_url)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            errores = {f: e.get_json_data() for f, e in form.errors.items()}
            primer_error = next(iter(form.errors.values()))[0]
            return JsonResponse({'error': primer_error}, status=400)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nuevo Nivel'
        ctx['accion'] = 'Crear nivel'
        return ctx


class NivelUpdateView(LoginRequiredMixin, AdminRequeridoMixin, UpdateView):
    model         = Nivel
    form_class    = NivelForm
    template_name = 'periodos/nivel_formulario.html'
    success_url   = reverse_lazy('periodos:nivel-lista')

    def form_valid(self, form):
        messages.success(self.request, f'Nivel "{form.instance.nombre}" actualizado.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar nivel: {self.object.nombre}'
        ctx['accion'] = 'Guardar cambios'
        return ctx


# ══════════════════════════════════════════════════════════════════════════════
#  PARALELO
# ══════════════════════════════════════════════════════════════════════════════

class ParaleloListView(LoginRequiredMixin, SecretariaRequeridaMixin, ListView):
    model               = Paralelo
    template_name       = 'periodos/paralelo_lista.html'
    context_object_name = 'paralelos'

    def get_queryset(self):
        qs = super().get_queryset().select_related('periodo', 'nivel')
        periodo_id = self.request.GET.get('periodo')
        if periodo_id:
            qs = qs.filter(periodo_id=periodo_id)
        else:
            activo = PeriodoAcademico.get_activo()
            if activo:
                qs = qs.filter(periodo=activo)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['periodos']    = PeriodoAcademico.objects.order_by('-fecha_inicio')
        ctx['periodo_sel'] = self.request.GET.get('periodo', '')
        return ctx


class ParaleloCreateView(LoginRequiredMixin, AdminRequeridoMixin, CreateView):
    model         = Paralelo
    form_class    = ParaleloForm
    template_name = 'periodos/paralelo_formulario.html'
    success_url   = reverse_lazy('periodos:paralelo-lista')

    def form_valid(self, form):
        messages.success(self.request, f'Paralelo "{form.instance}" creado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nuevo Paralelo'
        ctx['accion'] = 'Crear paralelo'
        return ctx


class ParaleloUpdateView(LoginRequiredMixin, AdminRequeridoMixin, UpdateView):
    model         = Paralelo
    form_class    = ParaleloForm
    template_name = 'periodos/paralelo_formulario.html'
    success_url   = reverse_lazy('periodos:paralelo-lista')

    def form_valid(self, form):
        messages.success(self.request, f'Paralelo "{form.instance}" actualizado.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object}'
        ctx['accion'] = 'Guardar cambios'
        return ctx


class ParaleloDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model         = Paralelo
    template_name = 'periodos/paralelo_confirmar_eliminar.html'
    success_url   = reverse_lazy('periodos:paralelo-lista')

    def form_valid(self, form):
        if self.object.matriculados_aprobados > 0:
            messages.error(
                self.request,
                f'No se puede eliminar: el paralelo tiene {self.object.matriculados_aprobados} estudiante(s) matriculado(s).'
            )
            return self.render_to_response(self.get_context_data())
        messages.warning(self.request, f'Paralelo "{self.object}" eliminado.')
        return super().form_valid(form)


# ══════════════════════════════════════════════════════════════════════════════
#  API REST (DRF)
# ══════════════════════════════════════════════════════════════════════════════
try:
    from rest_framework import viewsets, filters
    from rest_framework.decorators import action
    from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
    from rest_framework.response import Response
    from .serializers import (
        PeriodoAcademicoSerializer, NivelSerializer,
        ParaleloSerializer, ParaleloDetalleSerializer,
    )

    class PeriodoAcademicoViewSet(viewsets.ModelViewSet):
        queryset           = PeriodoAcademico.objects.all()
        serializer_class   = PeriodoAcademicoSerializer
        permission_classes = [IsAuthenticated]
        filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
        search_fields      = ['nombre']
        ordering_fields    = ['fecha_inicio', 'nombre']

        @action(detail=False, methods=['get'])
        def activo(self, request):
            periodo = PeriodoAcademico.get_activo()
            if not periodo:
                return Response({'detail': 'No hay período activo.'}, status=404)
            return Response(PeriodoAcademicoSerializer(periodo, context={'request': request}).data)

        @action(detail=True, methods=['get'])
        def paralelos(self, request, pk=None):
            periodo    = self.get_object()
            qs         = periodo.paralelos.select_related('nivel').order_by('nivel__orden', 'nombre')
            serializer = ParaleloDetalleSerializer(qs, many=True, context={'request': request})
            return Response(serializer.data)

    class NivelViewSet(viewsets.ModelViewSet):
        queryset           = Nivel.objects.all()
        serializer_class   = NivelSerializer
        permission_classes = [IsAuthenticated]

    class ParaleloViewSet(viewsets.ModelViewSet):
        queryset           = Paralelo.objects.select_related('periodo', 'nivel').all()
        permission_classes = [IsAuthenticated]

        def get_serializer_class(self):
            if self.action in ('retrieve', 'con_cupo'):
                return ParaleloDetalleSerializer
            return ParaleloSerializer

        def get_queryset(self):
            qs = super().get_queryset()
            periodo_id = self.request.query_params.get('periodo')
            if periodo_id:
                qs = qs.filter(periodo_id=periodo_id)
            return qs

        @action(detail=False, methods=['get'], url_path='con-cupo')
        def con_cupo(self, request):
            activo = PeriodoAcademico.get_activo()
            if not activo:
                return Response({'detail': 'No hay período activo.'}, status=404)
            paralelos  = self.get_queryset().filter(periodo=activo)
            con_cupo   = [p for p in paralelos if not p.cupo_lleno]
            serializer = ParaleloDetalleSerializer(con_cupo, many=True, context={'request': request})
            return Response(serializer.data)

except ImportError:
    pass
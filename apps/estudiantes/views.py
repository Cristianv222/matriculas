"""
============================================================
  MÓDULO: estudiantes — views.py
  CBVs para interfaz web + ViewSets para API REST
============================================================
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Estudiante
from .forms import EstudianteForm, EstudianteBusquedaForm


# ══════════════════════════════════════════════════════════════════════════════
#  VISTAS WEB (CBVs)
# ══════════════════════════════════════════════════════════════════════════════

class EstudianteListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model               = Estudiante
    template_name       = 'estudiantes/lista.html'
    context_object_name = 'estudiantes'
    paginate_by         = 20
    permission_required = 'estudiantes.view_estudiante'

    def get_queryset(self):
        qs   = super().get_queryset().select_related('representante')
        form = EstudianteBusquedaForm(self.request.GET)

        if form.is_valid():
            q = form.cleaned_data.get('q')
            if q:
                qs = qs.filter(
                    Q(nombres__icontains=q)
                    | Q(apellidos__icontains=q)
                    | Q(cedula__icontains=q)
                )
            if form.cleaned_data.get('genero'):
                qs = qs.filter(genero=form.cleaned_data['genero'])

            if form.cleaned_data.get('ciudad'):
                qs = qs.filter(ciudad__icontains=form.cleaned_data['ciudad'])

            if form.cleaned_data.get('atencion_especial'):
                qs = qs.filter(
                    Q(tiene_discapacidad=True)
                    | ~Q(enfermedades_cronicas='')
                    | ~Q(alergias='')
                )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['busqueda_form'] = EstudianteBusquedaForm(self.request.GET)
        ctx['total']         = self.get_queryset().count()
        return ctx


class EstudianteDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model               = Estudiante
    template_name       = 'estudiantes/detalle.html'
    context_object_name = 'estudiante'
    permission_required = 'estudiantes.view_estudiante'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.object
        # Matrículas del estudiante ordenadas
        ctx['matriculas'] = obj.matriculas.select_related(
            'paralelo', 'paralelo__periodo', 'revisado_por'
        ).order_by('-fecha_solicitud')
        return ctx


class EstudianteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model               = Estudiante
    form_class          = EstudianteForm
    template_name       = 'estudiantes/formulario.html'
    permission_required = 'estudiantes.add_estudiante'

    def get_success_url(self):
        return reverse_lazy('estudiantes:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Estudiante "{form.instance.nombre_completo}" creado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo']  = 'Registrar nuevo estudiante'
        ctx['accion']  = 'Registrar'
        return ctx


class EstudianteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model               = Estudiante
    form_class          = EstudianteForm
    template_name       = 'estudiantes/formulario.html'
    permission_required = 'estudiantes.change_estudiante'

    def get_success_url(self):
        return reverse_lazy('estudiantes:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Estudiante "{form.instance.nombre_completo}" actualizado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.nombre_completo}'
        ctx['accion'] = 'Guardar cambios'
        return ctx


class EstudianteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model               = Estudiante
    template_name       = 'estudiantes/confirmar_eliminar.html'
    success_url         = reverse_lazy('estudiantes:lista')
    permission_required = 'estudiantes.delete_estudiante'

    def form_valid(self, form):
        nombre = self.object.nombre_completo
        messages.warning(self.request, f'Estudiante "{nombre}" eliminado.')
        return super().form_valid(form)


# ══════════════════════════════════════════════════════════════════════════════
#  API REST (ViewSets con DRF)  — instalar: pip install djangorestframework
# ══════════════════════════════════════════════════════════════════════════════
try:
    from rest_framework import viewsets, filters, status
    from rest_framework.decorators import action
    from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
    from rest_framework.response import Response
    from django_filters.rest_framework import DjangoFilterBackend
    from .serializers import EstudianteSerializer, EstudianteListSerializer

    class EstudianteViewSet(viewsets.ModelViewSet):
        """
        API CRUD completa para Estudiantes.

        GET    /api/estudiantes/              → lista paginada
        POST   /api/estudiantes/              → crear
        GET    /api/estudiantes/{id}/         → detalle
        PUT    /api/estudiantes/{id}/         → actualizar completo
        PATCH  /api/estudiantes/{id}/         → actualizar parcial
        DELETE /api/estudiantes/{id}/         → eliminar
        GET    /api/estudiantes/{id}/matriculas/ → matrículas del estudiante
        GET    /api/estudiantes/atencion_especial/ → requieren atención especial
        """
        queryset           = Estudiante.objects.select_related('representante').all()
        permission_classes = [IsAuthenticated, DjangoModelPermissions]
        filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
        filterset_fields   = ['genero', 'etnia', 'ciudad', 'tiene_discapacidad', 'tipo_sangre']
        search_fields      = ['nombres', 'apellidos', 'cedula',
                              'padre_nombres', 'madre_nombres']
        ordering_fields    = ['apellidos', 'nombres', 'fecha_nacimiento', 'created_at']
        ordering           = ['apellidos', 'nombres']

        def get_serializer_class(self):
            if self.action == 'list':
                return EstudianteListSerializer
            return EstudianteSerializer

        @action(detail=True, methods=['get'], url_path='matriculas')
        def matriculas(self, request, pk=None):
            """Devuelve todas las matrículas del estudiante."""
            estudiante = self.get_object()
            from apps.matriculas.serializers import MatriculaSerializer
            matriculas = estudiante.matriculas.select_related(
                'paralelo', 'paralelo__periodo'
            ).order_by('-fecha_solicitud')
            serializer = MatriculaSerializer(matriculas, many=True, context={'request': request})
            return Response(serializer.data)

        @action(detail=False, methods=['get'], url_path='atencion-especial')
        def atencion_especial(self, request):
            """Lista de estudiantes que requieren atención especial."""
            qs = self.get_queryset().filter(
                Q(tiene_discapacidad=True)
                | ~Q(enfermedades_cronicas='')
                | ~Q(alergias='')
            )
            serializer = EstudianteListSerializer(qs, many=True, context={'request': request})
            return Response(serializer.data)

except ImportError:
    # DRF no instalado — las vistas web funcionan igual
    pass
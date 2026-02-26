"""
============================================================
  MÓDULO: usuarios — views.py
  Autenticación, registro, perfil + API ViewSets
============================================================
"""
import secrets
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, View, TemplateView
)
from .forms import (
    RegistroRepresentanteForm, PerfilForm, UsuarioAdminForm,
    UsuarioCreateForm, CambioPasswordForm, LoginForm,
)
from .models import Usuario, SesionUsuario


# ── Mixins de rol ─────────────────────────────────────────────────────────────

class AdminRequeridoMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.es_admin


class SecretariaRequeridaMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.es_secretaria


# ── Utilidad: registrar sesión ────────────────────────────────────────────────

def _registrar_sesion(request, usuario, exitosa=True):
    ip = (
        request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        or request.META.get('REMOTE_ADDR', '')
    )
    SesionUsuario.objects.create(
        usuario=usuario,
        ip=ip or '0.0.0.0',
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        exitosa=exitosa,
    )
    if exitosa:
        usuario.ultimo_acceso_ip = ip
        usuario.save(update_fields=['ultimo_acceso_ip'])


# ══════════════════════════════════════════════════════════════════════════════
#  AUTENTICACIÓN
# ══════════════════════════════════════════════════════════════════════════════

class LoginView(View):
    template_name = 'usuarios/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(self._get_dashboard(request.user))
        from django.shortcuts import render
        return render(request, self.template_name, {'form': LoginForm()})

    def post(self, request):
        from django.shortcuts import render
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # Permitir login con email o username
        if '@' in username:
            try:
                username = Usuario.objects.get(email__iexact=username).username
            except Usuario.DoesNotExist:
                pass

        user = authenticate(request, username=username, password=password)

        if user is None:
            # Intentar registrar intento fallido si el usuario existe
            try:
                u = Usuario.objects.get(username=username)
                _registrar_sesion(request, u, exitosa=False)
            except Usuario.DoesNotExist:
                pass
            messages.error(request, 'Credenciales incorrectas.')
            return render(request, self.template_name, {'form': form})

        if not user.is_active:
            messages.error(request, 'Tu cuenta está desactivada. Contacta a la secretaría.')
            return render(request, self.template_name, {'form': form})

        login(request, user)
        _registrar_sesion(request, user, exitosa=True)

        if not form.cleaned_data.get('recordarme'):
            request.session.set_expiry(0)  # Sesión expira al cerrar navegador

        messages.success(request, f'Bienvenido/a, {user.nombre_completo}.')
        return redirect(request.GET.get('next') or self._get_dashboard(user))

    @staticmethod
    def _get_dashboard(user):
        if user.es_admin or user.es_secretaria:
            return 'usuarios:dashboard-admin'
        if user.es_representante:
            return 'usuarios:dashboard-representante'
        return 'usuarios:perfil'


class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        # Registrar fecha de logout en la última sesión
        SesionUsuario.objects.filter(
            usuario=request.user,
            fecha_logout__isnull=True
        ).order_by('-fecha_login').first().__class__.objects.filter(
            usuario=request.user,
            fecha_logout__isnull=True,
        ).update(fecha_logout=timezone.now())
        logout(request)
        messages.info(request, 'Has cerrado sesión correctamente.')
        return redirect('usuarios:login')


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTRO DE REPRESENTANTE
# ══════════════════════════════════════════════════════════════════════════════

class RegistroView(CreateView):
    model         = Usuario
    form_class    = RegistroRepresentanteForm
    template_name = 'usuarios/registro.html'
    success_url   = reverse_lazy('usuarios:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('usuarios:perfil')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        # Generar token de verificación de email
        token = secrets.token_urlsafe(32)
        user.token_verificacion = token
        user.token_expiracion   = timezone.now() + timezone.timedelta(hours=24)
        user.save(update_fields=['token_verificacion', 'token_expiracion'])
        # TODO: enviar email de verificación con el token
        messages.success(
            self.request,
            'Cuenta creada. Revisa tu correo para verificar tu cuenta.'
        )
        return response


class VerificarEmailView(View):
    def get(self, request, token):
        try:
            user = Usuario.objects.get(token_verificacion=token)
        except Usuario.DoesNotExist:
            messages.error(request, 'Token de verificación inválido.')
            return redirect('usuarios:login')

        if user.token_expiracion and user.token_expiracion < timezone.now():
            messages.error(request, 'El token ha expirado. Solicita uno nuevo.')
            return redirect('usuarios:login')

        user.is_verified        = True
        user.token_verificacion = ''
        user.token_expiracion   = None
        user.save(update_fields=['is_verified', 'token_verificacion', 'token_expiracion'])
        messages.success(request, '¡Email verificado! Ya puedes iniciar sesión.')
        return redirect('usuarios:login')


# ══════════════════════════════════════════════════════════════════════════════
#  PERFIL DE USUARIO
# ══════════════════════════════════════════════════════════════════════════════

class PerfilView(LoginRequiredMixin, UpdateView):
    model         = Usuario
    form_class    = PerfilForm
    template_name = 'usuarios/perfil.html'
    success_url   = reverse_lazy('usuarios:perfil')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)


class CambioPasswordView(LoginRequiredMixin, View):
    template_name = 'usuarios/cambio_password.html'

    def get(self, request):
        from django.shortcuts import render
        return render(request, self.template_name, {'form': CambioPasswordForm(request.user)})

    def post(self, request):
        from django.shortcuts import render
        form = CambioPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantener sesión activa
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('usuarios:perfil')
        return render(request, self.template_name, {'form': form})


# ══════════════════════════════════════════════════════════════════════════════
#  GESTIÓN DE USUARIOS (Admin/Secretaria)
# ══════════════════════════════════════════════════════════════════════════════

class UsuarioListView(LoginRequiredMixin, SecretariaRequeridaMixin, ListView):
    model               = Usuario
    template_name       = 'usuarios/lista.html'
    context_object_name = 'usuarios'
    paginate_by         = 25

    def get_queryset(self):
        qs  = super().get_queryset()
        q   = self.request.GET.get('q', '')
        rol = self.request.GET.get('rol', '')
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(username__icontains=q)
                | Q(email__icontains=q)
                | Q(cedula__icontains=q)
            )
        if rol:
            qs = qs.filter(rol=rol)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['roles'] = Usuario.ROLES
        ctx['q']     = self.request.GET.get('q', '')
        ctx['rol']   = self.request.GET.get('rol', '')
        return ctx


class UsuarioCreateView(LoginRequiredMixin, AdminRequeridoMixin, CreateView):
    """El admin crea un usuario con cualquier rol desde el panel interno."""
    model         = Usuario
    form_class    = UsuarioCreateForm
    template_name = 'usuarios/formulario.html'
    success_url   = reverse_lazy('usuarios:lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nuevo usuario'
        ctx['accion'] = 'Crear usuario'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Usuario "{form.instance.get_full_name()}" creado correctamente.')
        return super().form_valid(form)


class UsuarioDetailView(LoginRequiredMixin, SecretariaRequeridaMixin, DetailView):
    model               = Usuario
    template_name       = 'usuarios/detalle.html'
    context_object_name = 'usuario_obj'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sesiones'] = self.object.sesiones.order_by('-fecha_login')[:20]
        # Si es representante, mostrar sus estudiantes
        if self.object.es_representante:
            ctx['estudiantes'] = self.object.estudiantes.all()
        return ctx


class UsuarioUpdateView(LoginRequiredMixin, AdminRequeridoMixin, UpdateView):
    model         = Usuario
    form_class    = UsuarioAdminForm
    template_name = 'usuarios/formulario.html'

    def get_success_url(self):
        return reverse_lazy('usuarios:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Usuario "{self.object.nombre_completo}" actualizado.')
        return super().form_valid(form)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARDS
# ══════════════════════════════════════════════════════════════════════════════



# =============================================================================
#  AJAX — ASIGNACIÓN DE ESTUDIANTES A REPRESENTANTE
# =============================================================================

class BuscarEstudianteView(LoginRequiredMixin, AdminRequeridoMixin, View):
    """GET /usuarios/usuarios/<pk>/buscar-estudiante/?cedula=..."""
    def get(self, request, pk):
        from apps.estudiantes.models import Estudiante
        cedula = request.GET.get('cedula', '').strip()
        if not cedula:
            return JsonResponse({'error': 'Ingrese una cédula.'}, status=400)
        try:
            est = Estudiante.objects.select_related('representante').get(cedula=cedula)
        except Estudiante.DoesNotExist:
            return JsonResponse({'error': f'No existe estudiante con cédula {cedula}.'}, status=404)

        rep = get_object_or_404(Usuario, pk=pk)
        if est.representante and est.representante.pk != rep.pk:
            return JsonResponse({
                'error': f'Ya asignado a: {est.representante.get_full_name()}.'
            }, status=409)

        return JsonResponse({
            'id': est.pk,
            'nombre': est.nombre_completo,
            'cedula': est.cedula or '—',
            'ya_asignado': est.representante_id == rep.pk,
            'relacion': est.relacion_representante,
        })


class AsignarEstudianteView(LoginRequiredMixin, AdminRequeridoMixin, View):
    """POST /usuarios/usuarios/<pk>/asignar-estudiante/  body: {estudiante_id: N}"""
    def post(self, request, pk):
        import json
        from apps.estudiantes.models import Estudiante
        try:
            data = json.loads(request.body)
            est_id = int(data.get('estudiante_id', 0))
        except Exception:
            return JsonResponse({'error': 'Datos inválidos.'}, status=400)

        rep = get_object_or_404(Usuario, pk=pk)
        est = get_object_or_404(Estudiante, pk=est_id)

        if est.representante and est.representante.pk != rep.pk:
            return JsonResponse({'error': 'Ya asignado a otro representante.'}, status=409)

        est.representante = rep
        est.save(update_fields=['representante'])
        return JsonResponse({
            'ok': True,
            'id': est.pk,
            'nombre': est.nombre_completo,
            'cedula': est.cedula or '—',
            'relacion': est.relacion_representante,
        })


class DesasignarEstudianteView(LoginRequiredMixin, AdminRequeridoMixin, View):
    """POST /usuarios/usuarios/<pk>/desasignar/<est_pk>/"""
    def post(self, request, pk, est_pk):
        from apps.estudiantes.models import Estudiante
        rep = get_object_or_404(Usuario, pk=pk)
        est = get_object_or_404(Estudiante, pk=est_pk, representante=rep)
        nombre = est.nombre_completo
        est.representante = None
        est.save(update_fields=['representante'])
        return JsonResponse({'ok': True, 'nombre': nombre})

class DashboardAdminView(LoginRequiredMixin, SecretariaRequeridaMixin, TemplateView):
    template_name = 'usuarios/dashboard_admin.html'

    def get_context_data(self, **kwargs):
        from apps.matriculas.models import Matricula
        from apps.periodos.models import PeriodoAcademico
        ctx             = super().get_context_data(**kwargs)
        periodo_activo  = PeriodoAcademico.get_activo()
        ctx['periodo']  = periodo_activo
        if periodo_activo:
            matriculas = Matricula.objects.filter(paralelo__periodo=periodo_activo)
            ctx['total_matriculas']     = matriculas.count()
            ctx['pendientes']           = matriculas.filter(estado=Matricula.ESTADO_PENDIENTE).count()
            ctx['en_revision']          = matriculas.filter(estado=Matricula.ESTADO_EN_REVISION).count()
            ctx['aprobadas']            = matriculas.filter(estado=Matricula.ESTADO_APROBADA).count()
            ctx['rechazadas']           = matriculas.filter(estado=Matricula.ESTADO_RECHAZADA).count()
        ctx['total_usuarios']       = Usuario.objects.filter(is_active=True).count()
        ctx['total_representantes'] = Usuario.objects.filter(rol=Usuario.ROL_REPRESENTANTE).count()
        return ctx


class DashboardRepresentanteView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/dashboard_representante.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.es_representante:
            return redirect('usuarios:dashboard-admin')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        from apps.periodos.models import PeriodoAcademico
        ctx = super().get_context_data(**kwargs)
        ctx['estudiantes']     = self.request.user.estudiantes.all()
        ctx['periodo_activo']  = PeriodoAcademico.get_activo()
        ctx['matriculas']      = self.request.user.matriculas_solicitadas.select_related(
            'estudiante', 'paralelo', 'paralelo__nivel', 'paralelo__periodo'
        ).order_by('-fecha_solicitud')[:10]
        return ctx


# ══════════════════════════════════════════════════════════════════════════════
#  API REST (DRF)
# ══════════════════════════════════════════════════════════════════════════════
try:
    from rest_framework import viewsets, filters, status
    from rest_framework.decorators import action
    from rest_framework.permissions import IsAuthenticated, IsAdminUser
    from rest_framework.response import Response
    from rest_framework.views import APIView
    from .serializers import UsuarioSerializer, UsuarioListSerializer

    class UsuarioViewSet(viewsets.ModelViewSet):
        """
        GET  /api/usuarios/              → lista (solo admin/secretaria)
        GET  /api/usuarios/yo/           → perfil del usuario autenticado
        POST /api/usuarios/{id}/activar/ → activar/desactivar cuenta
        """
        queryset           = Usuario.objects.all()
        permission_classes = [IsAuthenticated]
        filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
        search_fields      = ['username', 'first_name', 'last_name', 'email', 'cedula']
        ordering_fields    = ['last_name', 'first_name', 'date_joined']

        def get_serializer_class(self):
            if self.action == 'list':
                return UsuarioListSerializer
            return UsuarioSerializer

        def get_queryset(self):
            user = self.request.user
            if user.es_secretaria:
                return super().get_queryset()
            # Un representante o docente solo ve su propio perfil
            return super().get_queryset().filter(pk=user.pk)

        @action(detail=False, methods=['get', 'patch'])
        def yo(self, request):
            """Perfil del usuario autenticado."""
            if request.method == 'GET':
                return Response(UsuarioSerializer(request.user, context={'request': request}).data)
            serializer = UsuarioSerializer(
                request.user, data=request.data, partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        @action(detail=True, methods=['post'])
        def activar(self, request, pk=None):
            """Activa o desactiva un usuario (solo admin)."""
            if not request.user.es_admin:
                return Response({'detail': 'Sin permiso.'}, status=403)
            usuario = self.get_object()
            if usuario.is_superuser:
                return Response({'detail': 'No se puede modificar a un superusuario.'}, status=400)
            usuario.is_active = not usuario.is_active
            usuario.save(update_fields=['is_active'])
            estado = 'activado' if usuario.is_active else 'desactivado'
            return Response({'detail': f'Usuario {estado}.', 'is_active': usuario.is_active})

except ImportError:
    pass
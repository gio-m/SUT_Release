import os
from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView,DeleteView,TemplateView,UpdateView,  DetailView
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from juntadevecinos import settings
from .models import Profile, RegistroActividades, RegistroProyectos,Noticias,Propuesta,Proyectos,Actividades,Documentos
from .forms import CustomUserChangeForm, NoticiasForm, ActividadesForm, ProyectosForm, PropuestaForm,  FormularioDocumentos
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import pytz
from django.contrib.auth.models import User


from django.shortcuts import render
from .utils import get_coordinates

def geolocalizacion(request):
    if request.method == 'POST':
        address = request.POST.get('direccion')

        # Obtener las coordenadas
        latitude, longitude = get_coordinates(address)

        # Puedes hacer algo con las coordenadas aquí, como almacenarlas en la base de datos o mostrarlas en la página

        return render(request, 'resultado.html', {'latitude': latitude, 'longitude': longitude})

    return render(request, 'paginas/inicio.html')


def add_group_name_to_context(view_class):
    original_dispatch = view_class.dispatch

    def dispatch(self,request, *args, **kwargs):
        user = self.request.user
        group = user.groups.first()
        group_name = None
        color = None
        if group:
            if group.name == 'usuario':
                color = 'bg-primary'
            elif group.name == 'administrativo':
                color = 'bg-danger'
            elif group.name == 'directiva':
                color = 'bg-secondary'
            elif group.name == 'presidente':
                color = 'bg-success'

            group_name = group.name
        context ={
            'group_name': group_name,
            'color': color
        }
        self.extra_context = context
        return original_dispatch(self,request,*args,**kwargs)
    view_class.dispatch = dispatch
    return view_class




# Create your views here.

    class CustomTemplateview(TemplateView):
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            user = self.request.user
            group_name = None
            if user.is_authenticated:
                group = Group.objects.filter(user=user).first()
                if group:
                    group_name = group.name
                context ['group_name'] = group_name
                return context

def nosotros(request):
    return render(request, 'paginas/nosotros.html')


@add_group_name_to_context
class Homeview(TemplateView):
    template_name='paginas/inicio.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        noticias = Noticias.objects.all()
        vecino = self.request.user if self.request.user.is_authenticated else None

        context['noticias'] = noticias
        return context
@add_group_name_to_context
class Preguntasview(TemplateView):
    template_name='preguntas_frecuentes.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        return context 


@add_group_name_to_context
class CrearNoticiasView(CreateView):
    model = Noticias
    form_class = NoticiasForm
    template_name = 'crear_noticia.html'
    success_url = reverse_lazy('noticias')

    def form_valid(self, form):
        messages.success(self.request, 'Noticia guardada correctamente')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un error al guardar la Noticia')
        return self.render_to_response(self.get_context_data(form=form))


@add_group_name_to_context
class Crearview(TemplateView):
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        return context 

@add_group_name_to_context
class ErrorView(TemplateView):
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_image_path = os.path.join(settings.MEDIA_URL, 'error.png')
        context['error_image_path'] = error_image_path
        return context

@add_group_name_to_context
class Actividadesview(TemplateView):
    template_name='actividades.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        actividades = Actividades.objects.all()
        vecino = self.request.user if self.request.user.is_authenticated else None

        for item in actividades:
            if vecino:
                registro = RegistroActividades.objects.filter(actividad=item, vecino=vecino).first()
                item.is_enrolled = registro is not None
            else:
                item.is_enrolled = False
            
            enrollment_count = RegistroActividades.objects.filter(actividad=item).count()
            item.enrollment_count = enrollment_count

        context['actividades'] = actividades
        return context

@add_group_name_to_context
class Proyectosview(TemplateView):
    template_name='proyectos.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        proyectos = Proyectos.objects.all()
        vecino = self.request.user if self.request.user.is_authenticated else None

        for item in proyectos:
            if vecino:
                registro = RegistroProyectos.objects.filter(proyecto=item, vecino=vecino).first()
                item.is_enrolled = registro is not None
            else:
                item.is_enrolled = False
            
            enrollment_count = RegistroProyectos.objects.filter(proyecto=item).count()
            item.enrollment_count = enrollment_count

        context['proyectos'] = proyectos
        return context

    
@add_group_name_to_context
class Noticiasview(TemplateView):
    template_name='noticias.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        noticias = Noticias.objects.all()
        vecino = self.request.user if self.request.user.is_authenticated else None

        context['noticias'] = noticias
        return context

@add_group_name_to_context
class DocumentosView(UserPassesTestMixin,TemplateView):
    template_name='documentos.html'

    def test_func(self):
        allowed_groups = [ 'presidente', 'directiva']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        documentos = Documentos.objects.all()
        vecino = self.request.user if self.request.user.is_authenticated else None

        context['documentos'] = documentos
        return context
    

@add_group_name_to_context
class CrearActividades(UserPassesTestMixin, CreateView):
    model = Actividades
    form_class = ActividadesForm
    template_name = 'crear_actividades.html'
    success_url = reverse_lazy('actividades')
    
    def test_func(self):
        allowed_groups = [ 'presidente', 'directiva']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        messages.success(self.request, 'Actividad guardada correctamente')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un error al guardar la actividad')
        return self.render_to_response(self.get_context_data(form=form))

@add_group_name_to_context
class EditarActividad(UserPassesTestMixin, UpdateView):
    model = Actividades
    form_class = ActividadesForm
    template_name = 'editar_actividad.html'
    success_url = reverse_lazy('actividades')

    def test_func(self):
        allowed_groups = ['presidente', 'directiva']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'La actividad se ha actualizado satisfactoriamente')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar la actividad')
        return self.render_to_response(self.get_context_data(form=form))

# ELIMINACION DE UN REGISTRO
@add_group_name_to_context
class EliminarActividad(UserPassesTestMixin, DeleteView):
    model = Actividades
    template_name = 'eliminar_actividad.html'
    success_url = reverse_lazy('actividades')

    def test_func(self):
        allowed_groups = ['presidente', 'directiva']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        messages.success(self.request, 'La actividad se ha eliminado correctamente')
        return super().form_valid(form)

@add_group_name_to_context
class RegistroActividad(TemplateView):
    def get(self, request, actividad_id):
        actividad = get_object_or_404(Actividades, id=actividad_id)

        if request.user.is_authenticated and request.user.groups.first().name == 'usuario':
            vecino = request.user

            # Verificar si el usuario ya está inscrito en esta actividad
            ya_inscrito = RegistroActividades.objects.filter(actividad=actividad, vecino=vecino).exists()
            if ya_inscrito:
                messages.warning(request, 'Ya estás inscrito en esta actividad')
            else:
                inscripciones_count = RegistroActividades.objects.filter(actividad=actividad).count()
                if inscripciones_count < actividad.cupos:
                    # Si hay cupos disponibles, proceder con la inscripción
                    actividad.cupos+=1
                    registro = RegistroActividades(actividad=actividad, vecino=vecino)
                    registro.save()
                    
                    messages.success(request, 'Inscripción exitosa')
                else:
                    messages.error(request, 'No hay cupos disponibles para esta actividad')
        else:
            messages.error(request, 'No se pudo completar la inscripción')

        return redirect('actividades')

###### NOTICIAS #######
@add_group_name_to_context
class CrearNoticias(UserPassesTestMixin,CreateView):
    model = Noticias
    form_class = NoticiasForm
    template_name = 'crear_noticia.html'
    success_url = reverse_lazy('crear_noticia')
    def test_func(self):
        allowed_groups = ['presidente', 'directiva']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')
    def form_valid(self, form):
        messages.success(self.request, 'Noticia guardada correctamente')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un error al guardar la noticia')
        return self.render_to_response(self.get_context_data(form=form))

@add_group_name_to_context
class EditarNoticia(UserPassesTestMixin, UpdateView):
    model = Noticias
    form_class = NoticiasForm
    template_name = 'editar_noticia.html'
    success_url = reverse_lazy('noticias')

    def test_func(self):
        allowed_groups = ['presidente', 'directiva']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Noticia se ha actualizado satisfactoriamente')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar la noticia')
        return self.render_to_response(self.get_context_data(form=form))

# ELIMINACION DE UN REGISTRO
@add_group_name_to_context
class EliminarNoticia(UserPassesTestMixin, DeleteView):
    model = Noticias
    template_name = 'eliminar_noticia.html'
    success_url = reverse_lazy('noticias')

    def test_func(self):
        allowed_groups = ['presidente', 'directiva']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        messages.success(self.request, 'La noticia se ha eliminado correctamente')
        return super().form_valid(form)

#### PROYECTOS #####
@add_group_name_to_context
class CrearProyectos(UserPassesTestMixin,CreateView):
    model = Proyectos
    form_class = ProyectosForm
    template_name = 'crear_proyecto.html'
    success_url = reverse_lazy('crear_proyecto')
    def test_func(self):
        allowed_groups = ['presidente']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')
    def form_valid(self, form):
        messages.success(self.request, 'Proyecto guardado correctamente')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un error al guardar el proyecto')
        return self.render_to_response(self.get_context_data(form=form))
    
### EDICION DE PROYECTO
@add_group_name_to_context
class EditarProyecto(UserPassesTestMixin, UpdateView):
    model = Proyectos
    form_class = ProyectosForm
    template_name = 'editar_proyecto.html'
    success_url = reverse_lazy('proyectos')

    def test_func(self):
        allowed_groups = ['presidente']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'El proyecto se ha actualizado satisfactoriamente')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el proyecto')
        return self.render_to_response(self.get_context_data(form=form))

# ELIMINACION DE UN REGISTRO
@add_group_name_to_context
class EliminarProyecto(UserPassesTestMixin, DeleteView):
    model = Proyectos
    template_name = 'eliminar_proyecto.html'
    success_url = reverse_lazy('proyectos')

    def test_func(self):
        allowed_groups = ['presidente']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        messages.success(self.request, 'El proyecto se ha eliminado correctamente')
        return super().form_valid(form)

#CLAUDIO

@add_group_name_to_context
class EditarDocumento(UserPassesTestMixin, UpdateView):
    model = Documentos
    form_class = FormularioDocumentos
    template_name = 'editar_documento.html'
    success_url = reverse_lazy('documentos')

    def test_func(self):
        allowed_groups = ['presidente']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasar el usuario actual al formulario
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'El documento se ha actualizado satisfactoriamente')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el proyecto')
        return self.render_to_response(self.get_context_data(form=form))

@add_group_name_to_context
class SolicitudDocForm(UserPassesTestMixin, CreateView):
    model = Documentos
    form_class = FormularioDocumentos
    template_name = 'solicitud_documentos.html'
    success_url = reverse_lazy('solicitud_documentos')

    def test_func(self):
        allowed_groups = ['presidente', 'usuario']
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in allowed_groups)

    def handle_no_permission(self):
        return redirect('error')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasar el usuario actual al formulario
        return kwargs

    def form_valid(self, form):
        if 'estado' in form.cleaned_data:
            # Verificar si el usuario no tiene roles específicos y establecer el estado por defecto
            if not self.request.user.groups.filter(name='administrativo').exists() and not self.request.user.groups.filter(name='presidente').exists():
                form.instance.estado = 'P'  # Establecer el estado por defecto ('En progreso')
        
        messages.success(self.request, 'Solicitud enviada correctamente')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un error al enviar la solicitud')
        return self.render_to_response(self.get_context_data(form=form))
    

def register(request):
    data = {
        'form': CustomUserCreationForm()
    }

    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)

        if user_creation_form.is_valid():
            user_creation_form.save()

            user = authenticate(username=user_creation_form.cleaned_data['username'], password=user_creation_form.cleaned_data['password1'])
            login(request, user)
            return redirect('inicio')
        else:
            data['form'] = user_creation_form

    return render(request, 'registration/register.html', data)

User = get_user_model()

@add_group_name_to_context
class EditarUsuarioView(UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'registration/editar_usuario.html'
    success_url = reverse_lazy('inicio')

    def get_object(self, queryset=None):
        return self.request.user
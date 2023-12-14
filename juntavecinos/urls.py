from django.urls import include, path
from . import views
from .views import ErrorView, Homeview,Crearview,UpdateView,EditarActividad,EliminarActividad,EditarNoticia,EliminarNoticia,EditarProyecto,EliminarProyecto,CrearActividades,CrearProyectos,RegistroActividad,EditarDocumento
from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('', views.Homeview.as_view(), name='inicio'), 
    
    ###NOTICIAS###  
    path('noticias', views.Noticiasview.as_view(), name='noticias'),
    path('noticias/crear', login_required(views.CrearNoticias.as_view()), name='crear_noticia'),
    path('noticias/<int:pk>/editar/', login_required(EditarNoticia.as_view()), name='editar_noticia'),
    path('noticias/<int:pk>/eliminar/', login_required(EliminarNoticia.as_view()), name='eliminar_noticia'),

    ##ACTIVIDADES
    path('actividades', views.Actividadesview.as_view(), name='actividades'),
    path('actividades/crear', login_required(CrearActividades.as_view()), name='crear_actividades'),
    path('actividades/<int:pk>/editar/', login_required(EditarActividad.as_view()), name='editar_actividad'),
    path('actividades/<int:pk>/eliminar/', login_required(EliminarActividad.as_view()), name='eliminar_actividad'),
    ### REGISTRO ACTIVIDAD
    path('registro_actividad/<int:actividad_id>', login_required(RegistroActividad.as_view()), name='registro_actividad'),

    #### PROYECTOS###
    path('proyectos', views.Proyectosview.as_view(), name='proyectos'),
    path('proyectos/crear', login_required(CrearProyectos.as_view()), name='crear_proyecto'),
    path('proyectos/<int:pk>/editar/', login_required(EditarProyecto.as_view()), name='editar_proyecto'),
    path('proyectos/<int:pk>/eliminar/', login_required(EliminarProyecto.as_view()), name='eliminar_proyecto'),

###############################PREUGUNTAS FRECUENTES #############################
    path('preguntas_frecuentes', views.Preguntasview.as_view(), name='preguntas_frecuentes'),
    ### ERROR ###
    path('error/', login_required(ErrorView.as_view()), name='error'),
    #CLAUDIO, Kevin
    path('solicitud_documentos', views.SolicitudDocForm.as_view(), name='solicitud_documentos'),     
    path('documentos/', views.DocumentosView.as_view(), name='documentos'),
    path('documentos/<int:pk>/editar/', login_required(EditarDocumento.as_view()), name='editar_documento'),
    path('register/', views.register, name='register'),
    path('editar_usuario/', views.EditarUsuarioView.as_view(), name='editar_usuario'),


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)                 



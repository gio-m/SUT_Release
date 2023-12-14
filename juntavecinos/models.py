from django.db import models
from django.forms import PasswordInput
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
import pytz
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save 

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name="profile", verbose_name="usuario")
    direccion = models.CharField(max_length=255,null=True, blank=True, verbose_name="Direccion")
    localidad = models.CharField(max_length=255,null=True, blank=True, verbose_name="Localidad")
    telefono = models.CharField(max_length=55,null=True, blank=True,verbose_name="Telefono")
    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfiles"
        ordering = ['-id']

        def __str__(self) :
            return self.user.username
        
def created_user_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender,instance,**kwargs):
    instance.profile.save()

post_save.connect(created_user_profile,sender=User)
post_save.connect(save_user_profile,sender=User)

    
##Formato de base de datos para las noticias
class Noticias(models.Model):
    opciones_noticias =[
                        ['Seguridad', 'Seguridad'],
                        ['Programas educativos', 'Programas educativos'],
                        ['Eventos', 'Eventos'],
                        ['Mejoras de infraestructura', 'Mejoras de infraestructura'],
                        ['Comités de vecinos', 'Comités de vecinos'],
                        ['Otros', 'Otros'] 
                    ] 
    id = models.AutoField(primary_key=True)
    Titulo = models.CharField(max_length=100,verbose_name="Titulo")
    Tipo = models.CharField(max_length=100,choices=opciones_noticias, verbose_name="Tipo de noticia")
    Descripcion = models.TextField(verbose_name="Descripcion")
    Fecha = models.DateField(verbose_name="Fecha de publicación")
    Imagen = models.ImageField(upload_to='images/noticias/', verbose_name="Imagen")
    redactor = models.ForeignKey(User,on_delete=models.CASCADE, limit_choices_to={'groups__name': 'directiva'},verbose_name="Redactor")

    def __str__(self):
        fila = "Titulo: " + self.Titulo + '-' +"Descripcion : " + self.Descripcion + '-' +"Tipo de noticia: " + self.get_Tipo_display() + '-' +"Fecha de publicacion: " + self.Fecha 
        return fila
    def delete(self, using=None,keep_parents=False):
        self.Imagen.storage.delete(self.Imagen.name)
        super().delete();


##Formato de base de datos para las proyectos
class Proyectos(models.Model):
    opciones_proyectos =[
                        ['Seguridad', 'Seguridad'],
                        ['Programas educativos', 'Programas educativos'],
                        ['Eventos', 'Eventos'],
                        ['Mejoras de infraestructura', 'Mejoras de infraestructura'],
                        ['Comités de vecinos', 'Comités de vecinos'],
                        ['Otros', 'Otros'] 
                    ] 
    id = models.AutoField(primary_key=True)
    TipoProyecto = models.CharField(max_length=100,choices=opciones_proyectos,verbose_name="Tipo de proyecto")
    Descripcion = models.TextField(verbose_name="Descripcion")
    Imagen = models.ImageField(upload_to='images/proyectos/', verbose_name="Imagen")
    fecha_inicio = models.DateField(null=True, blank=True,verbose_name="Fecha de inicio de proyecto")
    encargado = models.ForeignKey(User,on_delete=models.CASCADE, limit_choices_to={'groups__name__in': ['directiva', 'presidente']},verbose_name="Encargado de la actividad",null=True, blank=True)

    def __str__(self):
        fila = "Tipo de proyecto: " + self.get_TipoProyecto_display() + '-' +"Descripcion : " + self.Descripcion
        return f"{fila}"
    def delete(self, using=None,keep_parents=False):
        self.Imagen.storage.delete(self.Imagen.name)
        super().delete()
    class Meta: 
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

##Formato de base de datos para las actividades
class Actividades(models.Model):
    opciones_estado =[
                        ['R', 'Registro'],
                        ['D', 'Desarrollo'],
                        ['F', 'Finalizado']
                    ]
    opciones_actividades =[
                        ['Eventos', 'Eventos'],
                        ['Programas educativos', 'Programas educativos'],
                        ['Deportes', 'Deportes'],
                        ['Concursos', 'Concursos'],
                        ['Comités de vecinos', 'Comités de vecinos'],
                        ['Otros', 'Otros'] 
                    ] 
    id = models.AutoField(primary_key=True)
    TipoSolicitud = models.CharField(max_length=100,choices=opciones_actividades, verbose_name="Tipo de Actividad")
    Descripcion = models.TextField(verbose_name="Descripcion")
    Imagen = models.ImageField(upload_to='images/actividades/', verbose_name="Imagen")
    fecha_actividad = models.DateField(verbose_name="Fecha de actividad")
    encargado = models.ForeignKey(User,on_delete=models.CASCADE, limit_choices_to={'groups__name': 'directiva'},verbose_name="Encargado de la actividad")
    estado = models.CharField(max_length=1, choices=opciones_estado,default='R',verbose_name='Estado')
    cupos = models.PositiveIntegerField(default=0, verbose_name='Cupos de inscripcion')

    def actualizar_cupos(self):
        inscripciones_count = RegistroActividades.objects.filter(actividad=self).count()
        if self.cupos > 0:
            self.cupos -= 1
        self.save()

    def __str__(self):
        fila = "Tipo de solicitud: " + self.get_TipoSolicitud_display() + '-' +"Descripcion : " + self.Descripcion
        return f"{fila}"
    def delete(self, using=None,keep_parents=False):
        self.Imagen.storage.delete(self.Imagen.name)
        super().delete()
    class Meta: 
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

class RegistroActividades(models.Model):
    actividad = models.ForeignKey(Actividades, on_delete=models.CASCADE, verbose_name="Actividades")
    vecino = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vecinos_registrations', limit_choices_to={'groups__name':'usuario'},verbose_name='Vecino')
    habilitado = models.BooleanField(default=True,verbose_name='Vecino regular')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.actividad.actualizar_cupos()
    
    def __str__(self) :
        return f'{self.vecino.username} - {self.actividad.TipoSolicitud}'

    class Meta: 
        verbose_name = 'Inscripcion'
        verbose_name_plural = 'Inscripciones'

#ASISTENCIAS
class AsistenciaActividades(models.Model):
    actividad = models.ForeignKey(Actividades,on_delete=models.CASCADE,verbose_name='Actividad')
    vecino = models.ForeignKey(User,on_delete=models.CASCADE,related_name='asistencias',limit_choices_to={'groups__name':'usuario'},verbose_name='Vecino')
    presente = models.BooleanField(default=False,blank=True,null=True,verbose_name='Presente')
    fecha = models.DateField(null=True, blank=True,verbose_name='Fecha')
    

    def __str__(self) :
        return f'Asistencia {self.id}'
    

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'

class RegistroProyectos(models.Model):
    proyecto = models.ForeignKey(Proyectos, on_delete=models.CASCADE, verbose_name="Proyectos")
    vecino = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vecinos_registrations_proyectos', limit_choices_to={'groups__name':'usuario'},verbose_name='Vecino')
    habilitado = models.BooleanField(default=True,verbose_name='Vecino regular')

    def __str__(self) :
        return f'{self.vecino.username} - {self.proyecto.TipoProyecto}'
    
    class Meta: 
        verbose_name = 'Inscripcion'
        verbose_name_plural = 'Inscripciones'
##Formato de base de datos para las propuestas
class Propuesta(models.Model):
    opciones_proyectos =[
                        [0, 'Seguridad'],
                        [1, 'Mejora de calles'],
                        [2, 'Eventos'],
                        [3, 'Mejoras de infraestructura'],
                        [4, 'Concursos'],
                        [5, 'Otros'] 
                    ] 
    id = models.AutoField(primary_key=True)
    TipoSolicitud = models.CharField(max_length=100,choices=opciones_proyectos, verbose_name="Tipo de propuesta")
    Descripcion = models.TextField(verbose_name="Descripcion")
    def __str__(self):
        fila = "Tipo de solicitud: " + self.get_TipoSolicitud_display() + '-' +"Descripcion : " + self.Descripcion
        return f"{fila}"
    def delete(self, using=None,keep_parents=False):
        super().delete()

#CLAUDIO
##Formato de base de datos para los documentos   



class Documentos(models.Model):
    
    nombre_documento = models.CharField(max_length=100, verbose_name="Nombre del Documento")
    opciones_estado =[
                        ['A', 'Aprobado'],
                        ['R', 'Rechazado'],
                        ['P', 'En progreso']
                    ]
    TIPO_DOCUMENTO_CHOICES = [
        ("Certificado de residencia", "Certificado de residencia"),
        ("Boleta", "Boleta"),
    ]

    tipo_documento = models.CharField(
        max_length=50,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de Documento"
    )

    fecha_publicacion = models.DateTimeField(
        verbose_name="Fecha de Publicación",
        editable=False,  
        
    )
    descripcion_documento = models.TextField(verbose_name="Descripción del Documento")
    archivo = models.FileField(upload_to='documentos/', verbose_name="Adjunta un documento que compruebe tu identidad.")
    estado = models.CharField(null=True, blank=True,max_length=1, choices=opciones_estado,default='P',verbose_name='Estado')
    def save(self, *args, **kwargs):
        if not self.fecha_publicacion:
            self.fecha_publicacion = timezone.now().astimezone(pytz.timezone("Chile/Continental"))
        super(Documentos, self).save(*args, **kwargs)

    def __str__(self):
        return f"Documento: {self.nombre_documento} ({self.get_tipo_documento_display()})"
    

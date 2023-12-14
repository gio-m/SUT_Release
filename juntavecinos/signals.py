from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Profile,RegistroActividades

@receiver(post_save,sender=Profile)
def add_user_to_usuarios_group(sender,instance,created,**kwargs):
    if created:
        try:
            usuarios = Group.objects.get(name="usuario")
        except Group.DoesNotExist:
            usuarios = Group.objects.create(name="usuario")
            usuarios = Group.objects.create(name="directiva")
            usuarios = Group.objects.create(name="presidente")
            usuarios = Group.objects.create(name="administrativo")
        instance.user.groups.add(usuarios)


@receiver(post_save, sender=RegistroActividades)
def actualizar_cupos_actividad(sender, instance, **kwargs):
    instance.actividad.actualizar_cupos()
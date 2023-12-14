from django.contrib import admin
from .models import Noticias,Propuesta,Proyectos,Actividades,Documentos,Profile,RegistroActividades,AsistenciaActividades


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user","direccion","localidad","telefono","user_group")
    search_fields = ("localidad","user__username","user__groups__name")
    list_filter = ("user__groups","localidad")

    def user_group(self,obj):
        return " - ".join([t.name for t in obj.user.groups.all().order_by('name')])

    user_group.short_description = 'Grupo'

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("vecino","actividad","habilitado")
admin.site.register(RegistroActividades,RegistrationAdmin)

class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("vecino","actividad","presente","fecha")
admin.site.register(AsistenciaActividades,AsistenciaAdmin)

# Register your models here.
admin.site.register(Noticias)
admin.site.register(Propuesta)
admin.site.register(Proyectos)
admin.site.register(Actividades)
#Claudio
admin.site.register(Documentos)

admin.site.register(Profile,ProfileAdmin)
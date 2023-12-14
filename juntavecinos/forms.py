from pyexpat import model
import pytz, re
from django.contrib.auth import get_user_model
from django import forms 
from .models import Noticias, Actividades, Proyectos, Propuesta, RegistroActividades, Documentos
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, widgets, DateTimeField, DateField, DateInput
from django.utils.timezone import now
from datetime import date

from django.utils.translation import gettext_lazy as _
from itertools import cycle

from django.core.validators import RegexValidator

class NoticiasForm(forms.ModelForm):
    Fecha = DateTimeField(widget=DateInput(attrs={'type': 'date', 'min': date.today().strftime('%Y-%m-%d')}),
                                   input_formats=('%Y-%m-%d',),
                                   required=True)
    class Meta:
        model = Noticias
        fields = '__all__'
class DateInput(forms.DateInput):
    input_type = 'date'


class ActividadesForm(forms.ModelForm): 
    fecha_actividad = DateTimeField(widget=DateInput(attrs={'type': 'date', 'min': date.today().strftime('%Y-%m-%d')}),
                                   input_formats=('%Y-%m-%d',),
                                   required=True)
    estado = forms.ChoiceField(choices=Actividades.opciones_estado, initial='R',label='Estado')
    
    class Meta:
        model = Actividades
        fields = ['TipoSolicitud','Descripcion','Imagen','fecha_actividad','encargado','estado','cupos']





class ProyectosForm(forms.ModelForm):
    fecha_inicio = DateTimeField(widget=DateInput(attrs={'type': 'date', 'min': date.today().strftime('%Y-%m-%d')}),
                                   input_formats=('%Y-%m-%d',),
                                   required=True)
    class Meta:
        model = Proyectos
        fields = ['TipoProyecto','Descripcion','Imagen','fecha_inicio','encargado']



class PropuestaForm(forms.ModelForm):
    
    class Meta:
        model = Propuesta
        fields = '__all__'


        
        
#CLAUDIO
def validate_file_size(value):
    filesize = value.size
    if filesize > 20 * 1024 * 1024:  # 20 MB
        raise ValidationError(_('El archivo no puede superar los 20 MB.'))

class FormularioDocumentos(forms.ModelForm):
    TIPO_DOCUMENTO_CHOICES = [
        ("", "Seleccionar tipo de documento --"),  
        ("Certificado de residencia", "Certificado de residencia"),
        ("Boleta", "Boleta"),
    ]

    tipo_documento = forms.ChoiceField(
        choices=TIPO_DOCUMENTO_CHOICES,
        label="Tipo de Documento",
        required=True,
    )

    archivo = forms.FileField(
        label="Adjunta un documento que compruebe tu identidad.",
        required=True,
        help_text="Se permite un tamaño máximo de 20 MB.",
        validators=[validate_file_size]  # Agrega la validación al campo archivo
    )

    class Meta:
        model = Documentos
        fields = ['nombre_documento', 'tipo_documento', 'descripcion_documento', 'archivo','estado']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FormularioDocumentos, self).__init__(*args, **kwargs)
        
        if user:
            if not user.groups.filter(name='administrativo').exists() and not user.groups.filter(name='presidente').exists():
                self.fields['estado'].widget.attrs['readonly'] = True
                self.fields['estado'].widget.attrs['disabled'] = True
        

    def clean_tipo_documento(self):
        tipo_documento = self.cleaned_data.get('tipo_documento')
        if tipo_documento == "":
            raise forms.ValidationError("Debes seleccionar un tipo de documento")
        return tipo_documento
    


    
class CustomUserCreationForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
	def clean_email(self):
		email = self.cleaned_data['email']

		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('Este correo electrónico ya está registrado')
		return email
     
User = get_user_model()

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
	
    
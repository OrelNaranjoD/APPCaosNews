from django import forms
from django.core.validators import EmailValidator
from django.forms import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Noticia, DetalleNoticia, Comentario, Comentario

User = get_user_model()


class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo_noticia', 'cuerpo_noticia', 'id_categoria', 'id_pais', 'activo', 'destacada']

    def clean_id_pais(self):
        """Convierte cadena vacía a None para id_pais"""
        id_pais = self.cleaned_data.get('id_pais')
        if id_pais == '' or id_pais is None:
            return None
        return id_pais


class DetalleNoticiaForm(forms.ModelForm):
    class Meta:
        model = DetalleNoticia
        fields = ['comentario', 'estado', 'publicada', 'id_usuario']


class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo del usuario', max_length=100)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    first_name = forms.CharField(label='Nombre', max_length=100)
    last_name = forms.CharField(label='Apellido', max_length=100)
    username = forms.CharField(label='Nombre de usuario', max_length=100)
    email = forms.CharField(label='Correo electrónico', max_length=100, validators=[EmailValidator()])
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Validar la contraseña usando los validadores de Django
            from django.contrib.auth.password_validation import validate_password
            from django.contrib.auth import get_user_model
            user_model = get_user_model()
            try:
                validate_password(password, user_model())
            except ValidationError as error:
                raise forms.ValidationError(error.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe tu comentario aquí...',
                'maxlength': 500
            })
        }
        labels = {
            'contenido': 'Comentario'
        }

    def clean_contenido(self):
        contenido = self.cleaned_data.get('contenido')
        if not contenido or not contenido.strip():
            raise forms.ValidationError('El comentario no puede estar vacío.')
        if len(contenido.strip()) < 5:
            raise forms.ValidationError('El comentario debe tener al menos 5 caracteres.')
        return contenido.strip()


class RespuestaComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 2,
                'placeholder': 'Escribe tu respuesta...',
                'maxlength': 500
            })
        }
        labels = {
            'contenido': ''
        }

    def clean_contenido(self):
        contenido = self.cleaned_data.get('contenido')
        if not contenido or not contenido.strip():
            raise forms.ValidationError('La respuesta no puede estar vacía.')
        if len(contenido.strip()) < 3:
            raise forms.ValidationError('La respuesta debe tener al menos 3 caracteres.')
        return contenido.strip()

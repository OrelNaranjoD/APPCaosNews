from django import forms
from django.core.validators import EmailValidator
from django.forms import ValidationError
from .models import Noticia, Usuario

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = '__all__'
        
class LoginForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=100)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

class RegisterForm(forms.Form):
    first_name = forms.CharField(label='Nombre', max_length=100)
    last_name = forms.CharField(label='Apellido', max_length=100)
    username = forms.CharField(label='Nombre de usuario', max_length=100)
    email = forms.CharField(label='Correo electrónico', max_length=100, validators=[EmailValidator()])
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        
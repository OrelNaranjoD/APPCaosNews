from django import forms
from django.core.validators import EmailValidator, RegexValidator
from .models import Noticia

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = '__all__'
        
class LoginForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=100)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=100)
    email = forms.CharField(label='Correo electrónico', max_length=100, validators=[EmailValidator()])
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    phone_number = forms.CharField(label='Número telefónico', max_length=15, validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="El número telefónico debe tener un formato válido.")])

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return cleaned_data
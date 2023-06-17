from django.db import models
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import AbstractUser

class Noticia(models.Model):
    id_noticia  = models.AutoField(db_column='id_noticia', primary_key=True) 
    titulo_noticia = models.CharField(max_length=100, blank=False, null=False)
    cuerpo_noticia = models.TextField(blank=False, null=False, default='')
    id_categoria = models.ForeignKey('Categoria',on_delete=models.CASCADE, db_column='id_categoria')
    activo = models.BooleanField(("Activo"), default=True)
    imagen = models.ImageField(upload_to='news', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='id_usuario')
    
    def __str__(self):
        return self.titulo_noticia

class Categoria(models.Model):
    id_categoria = models.AutoField(db_column='id_categoria', primary_key=True) 
    nombre_categoria = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return str(self.nombre_categoria)
    
class Profile(models.Model):
    ROLES = (
        ('administrador', 'Administrador'),
        ('editor', 'Editor'),
        ('periodista', 'Periodista'),
        ('lector', 'Lector'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=ROLES, default='lector')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
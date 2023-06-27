from django.db import models
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Noticia(models.Model):
    id_noticia = models.AutoField(db_column='id_noticia', primary_key=True)
    titulo_noticia = models.CharField(max_length=100, blank=False, null=False)
    cuerpo_noticia = models.TextField(blank=False, null=False, default='')
    id_categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT, db_column='id_categoria')
    activo = models.BooleanField(("Activo"), default=True)
    
    def get_image_upload_path(instance, filename):
        extension = filename.split('.')[-1]
        return f"news/{instance.id_noticia}.{extension}"
    
    imagen = models.ImageField(upload_to=get_image_upload_path, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='id_usuario')
    delete = models.BooleanField(("Borrado"), default=False)
    
    def __str__(self):
        return self.titulo_noticia


@receiver(post_save, sender=Noticia)
def generate_image_filename(sender, instance, created, **kwargs):
    if created:
        instance.imagen.name = f"news/{instance.id_noticia}.{instance.imagen.name.split('.')[-1]}"
        instance.save()


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

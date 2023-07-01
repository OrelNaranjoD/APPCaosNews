from django.db import models
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import AbstractUser, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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
    eliminado = models.BooleanField(("Borrado"), default=False)
    
    def __str__(self):
        return self.titulo_noticia

@receiver(post_save, sender=Noticia)
def generate_image_filename(sender, instance, created, **kwargs):
    if created and instance.imagen:
        current_path = instance.imagen.path
        extension = os.path.splitext(current_path)[-1]
        new_filename = f"{instance.id_noticia}{extension}"
        new_path = os.path.join(os.path.dirname(current_path), new_filename)
        os.rename(current_path, new_path)
        instance.imagen.name = f"news/{new_filename}"
        instance.save()

class Categoria(models.Model):
    id_categoria = models.AutoField(db_column='id_categoria', primary_key=True)
    nombre_categoria = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return str(self.nombre_categoria)


class Usuario(AbstractUser):
    ROLES = (
        ('administrador', 'Administrador'),
        ('editor', 'Editor'),
        ('periodista', 'Periodista'),
        ('lector', 'Lector'),
    )

    role = models.CharField(max_length=15, choices=ROLES, default='lector')

    def __str__(self):
        return self.username

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
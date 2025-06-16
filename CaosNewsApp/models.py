from django.db import models
from django.conf import settings
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def get_image_upload_path(instance, filename):
    base_path = 'news'
    news_id = instance.noticia.id_noticia
    existing_images = instance.noticia.imagenes.count()
    new_filename = f"{news_id}-{existing_images + 1}{os.path.splitext(filename)[1]}"
    return os.path.join(base_path, str(news_id), new_filename)

class Noticia(models.Model):
    id_noticia = models.AutoField(db_column='id_noticia', primary_key=True)
    titulo_noticia = models.CharField(max_length=100, blank=False, null=False)
    cuerpo_noticia = models.TextField(blank=False, null=False, default='')
    id_categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT, db_column='id_categoria')
    id_pais = models.ForeignKey('Pais', on_delete=models.PROTECT, db_column='id_pais', null=True)
    activo = models.BooleanField(("Activo"), default=True)
    destacada = models.BooleanField(("Destacada"), default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='id_usuario')
    eliminado = models.BooleanField(("Borrado"), default=False)

    def __str__(self):
        return self.titulo_noticia

class DetalleNoticia(models.Model):
    id_detalle = models.AutoField(db_column='id_detalle', primary_key=True)
    noticia = models.OneToOneField(Noticia, on_delete=models.CASCADE, related_name='detalle')
    comentario = models.TextField(blank=True, null=True)
    ESTADO_CHOICES = (
        ('A', 'Aprobado'),
        ('R', 'Rechazado'),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, blank=True, null=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    publicacion = models.DateTimeField(blank=True, null=True, default=None)
    publicada = models.BooleanField(default=False)

    def __str__(self):
        return f'Detalle {self.id_detalle} - Noticia: {self.noticia.titulo_noticia}'


@receiver(post_save, sender=Noticia)
def create_detalle_noticia(sender, instance, created, **kwargs):
    if created:
        DetalleNoticia.objects.create(
            noticia=instance,
            id_usuario=instance.id_usuario  # Asignar el mismo usuario que creó la noticia
        )

class ImagenNoticia(models.Model):
    id_imagen = models.AutoField(db_column='id_imagen', primary_key=True)
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to=get_image_upload_path, null=True, blank=True)

    def __str__(self):
        return f'Imagen {self.id_imagen} - Noticia: {self.noticia.titulo_noticia}'

class Pais(models.Model):
    id_pais = models.AutoField(db_column='id_pais', primary_key=True)
    pais = models.CharField(max_length=20, blank=True, null=False)

    def __str__(self):
        return self.pais

class Categoria(models.Model):
    id_categoria = models.AutoField(db_column='id_categoria', primary_key=True)
    nombre_categoria = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return str(self.nombre_categoria)

class Comentario(models.Model):
    id_comentario = models.AutoField(db_column='id_comentario', primary_key=True)
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='id_usuario')
    contenido = models.TextField(max_length=500, blank=False, null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    # Soporte para comentarios anidados (respuestas)
    comentario_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas')

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f'Comentario de {self.usuario.first_name} {self.usuario.last_name} en {self.noticia.titulo_noticia}'

    @property
    def es_respuesta(self):
        """Retorna True si este comentario es una respuesta a otro comentario"""
        return self.comentario_padre is not None

    def get_respuestas(self):
        """Obtiene todas las respuestas activas a este comentario"""
        return self.respuestas.filter(activo=True).order_by('fecha_creacion')


class Plan(models.Model):
    """Modelo para planes de suscripción"""
    id_plan = models.AutoField(db_column='id_plan', primary_key=True)
    nombre = models.CharField(max_length=50, blank=False, null=False)
    descripcion = models.TextField(blank=True, default='')
    caracteristicas = models.TextField(blank=True, default='', help_text='Una característica por línea')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    @property
    def caracteristicas_list(self):
        """Convierte las características de texto a lista"""
        if self.caracteristicas:
            return [caracteristica.strip() for caracteristica in self.caracteristicas.split('\n') if caracteristica.strip()]
        return []

    @property
    def precio_mensual(self):
        """Obtiene el precio mensual del plan"""
        precio_mensual_obj = self.precios.filter(duracion_dias=30, activo=True).first()
        return precio_mensual_obj.valor if precio_mensual_obj else 0

    @property
    def precio_anual(self):
        """Obtiene el precio anual del plan"""
        precio_anual_obj = self.precios.filter(duracion_dias=365, activo=True).first()
        return precio_anual_obj.valor if precio_anual_obj else None

    @property
    def ahorro_anual(self):
        """Calcula el ahorro anual comparado con pagar mensual"""
        if self.precio_anual and self.precio_mensual:
            precio_anual_mensual = self.precio_mensual * 12
            return precio_anual_mensual - self.precio_anual
        return 0

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Planes'


class PrecioPlan(models.Model):
    """Modelo para precios de planes con diferentes duraciones personalizables"""
    id_precio = models.AutoField(db_column='id_precio', primary_key=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='precios')
    nombre_periodo = models.CharField(
        max_length=50,
        help_text="Nombre del período (ej: Mensual, Trimestral, Semestral, Anual, etc.)"
    )
    duracion_dias = models.PositiveIntegerField(
        help_text="Duración en días del período de suscripción"
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.plan.nombre} - {self.nombre_periodo} ({self.duracion_dias} días) - ${self.valor}'

    @property
    def precio_por_dia(self):
        """Calcula el precio por día"""
        return self.valor / self.duracion_dias if self.duracion_dias > 0 else 0

    @property
    def ahorro_vs_mensual(self):
        """Calcula el ahorro comparado con el precio mensual (30 días)"""
        precio_mensual = self.plan.precios.filter(duracion_dias=30, activo=True).first()
        if precio_mensual and self.duracion_dias > 30:
            precio_equivalente_mensual = (precio_mensual.valor * self.duracion_dias) / 30
            ahorro = precio_equivalente_mensual - self.valor
            return ahorro if ahorro > 0 else 0
        return 0

    @property
    def porcentaje_ahorro(self):
        """Calcula el porcentaje de ahorro comparado con el precio mensual"""
        precio_mensual = self.plan.precios.filter(duracion_dias=30, activo=True).first()
        if precio_mensual and self.duracion_dias > 30:
            precio_equivalente_mensual = (precio_mensual.valor * self.duracion_dias) / 30
            if precio_equivalente_mensual > 0:
                return ((precio_equivalente_mensual - self.valor) / precio_equivalente_mensual) * 100
        return 0

    class Meta:
        verbose_name = 'Precio de Plan'
        verbose_name_plural = 'Precios de Planes'
        unique_together = ['plan', 'nombre_periodo']  # Un solo precio por nombre de período por plan
        ordering = ['plan', 'duracion_dias']


class Suscripcion(models.Model):
    """Modelo para suscripciones de usuarios"""
    ESTADO_CHOICES = (
        ('A', 'Activa'),
        ('V', 'Vencida'),
        ('C', 'Cancelada'),
        ('P', 'Pendiente'),
    )

    id_suscripcion = models.AutoField(db_column='id_suscripcion', primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suscripciones')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    precio_plan = models.ForeignKey(PrecioPlan, on_delete=models.PROTECT, help_text="Precio específico pagado")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='A')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Suscripción {self.id_suscripcion} - {self.usuario.username} - {self.plan.nombre}'

    @property
    def esta_activa(self):
        """Verifica si la suscripción está activa y no ha vencido"""
        return self.estado == 'A' and self.fecha_fin > timezone.now()

    @property
    def dias_restantes(self):
        """Calcula los días restantes hasta la expiración"""
        if self.fecha_fin > timezone.now():
            return (self.fecha_fin - timezone.now()).days
        return 0

    @property
    def esta_proxima_a_vencer(self):
        """Verifica si la suscripción está próxima a vencer (3 días o menos)"""
        return self.esta_activa and self.dias_restantes <= 3

    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'
        ordering = ['-fecha_creacion']

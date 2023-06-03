from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.deletion import SET_NULL

class Noticia(models.Model):
    id_noticia = models.AutoField(primary_key=True)
    titulo_noticia = models.CharField(max_length=20, default='')
    subtitulo_noticia = models.CharField(max_length=50, default='')
    cuerpo_noticia = models.CharField(max_length=500, default='')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo_noticia

    # Opcional: añadir los Meta options según tus necesidades
    class Meta:
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'
    
class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('admin'  , 'Administrador' ),
        ('editor'  , 'Editor'),
        ('periodista', 'Periodista'),
        ('colaborador', 'Colaborador'),
        ('suscriptor' ,'Suscriptor'),

    )
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='suscriptor' )


 # Asegúrate de que no haya conflicto de nombres con 'auth.Group.user'
    user_groups = models.ManyToManyField(
        Group,
        related_name='custom_users',
        related_query_name='custom_user',
        blank=True,
        verbose_name='User groups'
    )
    
    # Asegúrate de que no haya conflicto de nombres con 'auth.User.groups'
    custom_user_groups = models.ManyToManyField(
        'self',
        related_name='group_members',
        related_query_name='group_member',
        symmetrical=False,
        blank=True,
        verbose_name='Custom user groups'
    )
    
    # Asegúrate de que no haya conflicto de nombres con 'auth.User.user_permissions'
    custom_user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users',
        related_query_name='custom_user',
        blank=True,
        verbose_name='Custom user permissions'
    )
    
    # Asegúrate de que no haya conflicto de nombres con 'auth.User.groups'
    groups = models.ManyToManyField(
        Group,
        related_name='custom_users_set',
        related_query_name='custom_user_set',
        blank=True,
        verbose_name='Groups',
        help_text='The groups this user belongs to.',
        symmetrical=False,
    )

    # Asegúrate de que no haya conflicto de nombres con 'auth.User.user_permissions'
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users_set',
        related_query_name='custom_user_set',
        blank=True,
        verbose_name='User permissions',
        help_text='Specific permissions for this user.',
        symmetrical=False,
    )
'''class Alumno(models.Model):
    rut = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=20)
    apellido_paterno = models.CharField(max_length=20)
    apellido_materno = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField(blank=False, null=False)
    id_genero = models.ForeignKey('Genero',on_delete=models.CASCADE, db_column='idGenero')
    telefono = models.CharField(max_length=45)
    email = models.EmailField(unique=True, max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=50, blank=True, null=True)
    activo = models.IntegerField()
    
    def __str__(self):
        return str(self.nombre)+" "+str(self.apellido_paterno)
'''
# Generated manually to set up user groups and permissions
# This migration creates the necessary groups for the application

from django.db import migrations
from django.contrib.auth.management import create_permissions


def create_user_groups(apps, schema_editor):
    '''
    Crea los grupos de usuarios necesarios para la aplicación
    '''
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Asegurar que los permisos estén creados
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None

    # Definir grupos y sus permisos
    groups_permissions = {
        'Administrador': [
            # Permisos completos para todos los modelos
            'add_noticia', 'change_noticia', 'delete_noticia', 'view_noticia',
            'add_categoria', 'change_categoria', 'delete_categoria', 'view_categoria',
            'add_pais', 'change_pais', 'delete_pais', 'view_pais',
            'add_imagennoticia', 'change_imagennoticia', 'delete_imagennoticia', 'view_imagennoticia',
            'add_detallenoticia', 'change_detallenoticia', 'delete_detallenoticia', 'view_detallenoticia',
            # Permisos de usuario
            'add_user', 'change_user', 'delete_user', 'view_user',
            'add_group', 'change_group', 'delete_group', 'view_group',
        ],
        'Editor': [
            # Permisos de edición y publicación
            'add_noticia', 'change_noticia', 'view_noticia',
            'view_categoria', 'view_pais',
            'add_imagennoticia', 'change_imagennoticia', 'delete_imagennoticia', 'view_imagennoticia',
            'add_detallenoticia', 'change_detallenoticia', 'view_detallenoticia',
            'view_user',
        ],
        'Periodista': [
            # Permisos para crear y editar noticias
            'add_noticia', 'change_noticia', 'view_noticia',
            'view_categoria', 'view_pais',
            'add_imagennoticia', 'change_imagennoticia', 'view_imagennoticia',
            'view_detallenoticia',
        ],
        'Lector': [
            # Solo permisos de lectura
            'view_noticia', 'view_categoria', 'view_pais',
        ]
    }

    print('Creando grupos de usuarios...')

    for group_name, permission_codenames in groups_permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f'Grupo creado: {group_name}')
        else:
            print(f'Grupo ya existe: {group_name}')

        # Asignar permisos al grupo
        permissions = []
        for codename in permission_codenames:
            try:
                perm = Permission.objects.get(codename=codename)
                permissions.append(perm)
            except Permission.DoesNotExist:
                print(f'Permiso no encontrado: {codename}')

        group.permissions.set(permissions)
        print(f'Permisos asignados al grupo {group_name}: {len(permissions)}')


def reverse_create_groups(apps, schema_editor):
    '''
    Elimina los grupos creados
    '''
    Group = apps.get_model('auth', 'Group')
    group_names = ['Administrador', 'Editor', 'Periodista', 'Lector']

    for group_name in group_names:
        try:
            group = Group.objects.get(name=group_name)
            group.delete()
            print(f'Grupo eliminado: {group_name}')
        except Group.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('CaosNewsApp', '0025_setup_user_groups'),
    ]

    operations = [
        # Crear grupos y permisos
        migrations.RunPython(
            create_user_groups,
            reverse_create_groups,
        ),
    ]

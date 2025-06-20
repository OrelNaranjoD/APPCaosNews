# Generated by Django 5.1.7 on 2025-06-08 21:17
# Modified to setup user groups for production environment

from django.db import migrations


def create_user_groups(apps, schema_editor):
    """
    Crea los grupos de usuarios necesarios para el sistema.
    """
    group_model = apps.get_model('auth', 'Group')

    # Crear grupos basicos
    groups_to_create = [
        'Administrador',
        'Editor',
        'Periodista',
        'Lector'
    ]

    for group_name in groups_to_create:
        group_model.objects.get_or_create(name=group_name)

def remove_user_groups(apps, schema_editor):
    """
    Funcion de reversa - elimina los grupos creados
    """
    group_model = apps.get_model('auth', 'Group')
    group_names = ['Administrador', 'Editor', 'Periodista', 'Lector']

    for name in group_names:
        try:
            group_model.objects.get(name=name).delete()
            print(f"Grupo eliminado: {name}")
        except group_model.DoesNotExist:
            print(f"Grupo no encontrado: {name}")


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('CaosNewsApp', '0024_delete_usuario'),
    ]

    operations = [
        migrations.RunPython(
            create_user_groups,
            remove_user_groups,
        ),
    ]

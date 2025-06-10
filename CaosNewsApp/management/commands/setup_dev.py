"""
Comando para configurar el entorno de desarrollo:
- Clona la base de datos de producción
- Agrega usuarios esenciales de desarrollo
- Copia los archivos media necesarios
"""

import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Configura el entorno de desarrollo clonando la base de datos de producción y agregando usuarios esenciales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-clone',
            action='store_true',
            help='Omite la clonación de la base de datos de producción',
        )
        parser.add_argument(
            '--skip-media',
            action='store_true',
            help='Omite la copia de archivos media',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Configurando entorno de desarrollo...')
        )

        base_dir = Path(settings.BASE_DIR)

        # Rutas de las bases de datos
        prod_db = base_dir / 'db.sqlite3'
        dev_db = base_dir / 'db_dev.sqlite3'

        # Rutas de archivos media
        prod_media = base_dir / 'media'
        dev_media = base_dir / 'media_dev'

        # 1. Clonar base de datos de producción
        if not options['skip_clone']:
            self.clone_production_database(prod_db, dev_db)
        else:
            self.stdout.write(
                self.style.WARNING('⏭️  Omitiendo clonación de base de datos')
            )

        # 2. Copiar archivos media
        if not options['skip_media']:
            self.copy_media_files(prod_media, dev_media)
        else:
            self.stdout.write(
                self.style.WARNING('⏭️  Omitiendo copia de archivos media')
            )

        # 5. Crear usuarios esenciales de desarrollo
        self.create_dev_users()

        # 6. Crear directorios necesarios
        self.create_directories()

        self.stdout.write(
            self.style.SUCCESS('✅ Entorno de desarrollo configurado correctamente!')
        )
        self.display_dev_users_info()

    def clone_production_database(self, prod_db, dev_db):
        """Clona la base de datos de producción para desarrollo"""
        try:
            if prod_db.exists():
                self.stdout.write('📋 Clonando base de datos de producción...')

                # Remover base de datos DEV existente si existe
                if dev_db.exists():
                    dev_db.unlink()
                    self.stdout.write('🗑️  Base de datos de desarrollo anterior removida')

                # Copiar base de datos de producción
                shutil.copy2(prod_db, dev_db)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Base de datos clonada: {dev_db}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Base de datos de producción no encontrada: {prod_db}')
                )
                self.stdout.write('📋 Creando nueva base de datos de desarrollo...')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error clonando base de datos: {e}')
            )
            # Crear nueva base de datos si falla la copia
            self.stdout.write('📋 Creando nueva base de datos de desarrollo...')

    def copy_media_files(self, prod_media, dev_media):
        """Copia archivos media de producción para desarrollo"""
        try:
            if prod_media.exists():
                self.stdout.write('📁 Copiando archivos media...')

                # Remover directorio DEV media existente si existe
                if dev_media.exists():
                    shutil.rmtree(dev_media)
                    self.stdout.write('🗑️  Directorio media de desarrollo anterior removido')

                # Copiar directorio media de producción
                shutil.copytree(prod_media, dev_media)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Archivos media copiados: {dev_media}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Directorio media de producción no encontrado: {prod_media}')
                )
                # Crear directorio vacío
                dev_media.mkdir(exist_ok=True)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error copiando archivos media: {e}')
            )
            # Crear directorio vacío si falla la copia
            dev_media.mkdir(exist_ok=True)

    @transaction.atomic
    def create_dev_users(self):
        """Crea usuarios esenciales para desarrollo (NO datos de prueba)"""
        User = get_user_model()

        self.stdout.write('👥 Creando usuarios esenciales de desarrollo...')

        # Crear grupos si no existen
        self.create_user_groups()

        # Solo usuarios esenciales para desarrollo (sin campo 'role' porque usa auth.User)
        dev_users = [
            # Superusuario principal de desarrollo
            {
                'username': 'devadmin',
                'email': 'devadmin@caosnews.com',
                'password': 'devpass123',
                'first_name': 'Dev',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            },
            # Usuario de desarrollo para pruebas de funcionalidad
            {
                'username': 'devuser',
                'email': 'devuser@caosnews.com',
                'password': 'devuser123',
                'first_name': 'Dev',
                'last_name': 'User',
                'is_staff': False,
                'is_superuser': False,
            },
            # Periodista de desarrollo
            {
                'username': 'devperiodista',
                'email': 'devperiodista@caosnews.com',
                'password': 'devper123',
                'first_name': 'Dev',
                'last_name': 'Periodista',
                'is_staff': True,
                'is_superuser': False,
            },
        ]

        created_users = []
        for user_data in dev_users:
            username = user_data['username']

            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                # Actualizar usuario existente
                user = User.objects.get(username=username)
                for field, value in user_data.items():
                    if field == 'password':
                        user.set_password(value)  # Django hashea automáticamente la contraseña
                    else:
                        setattr(user, field, value)
                user.save()
                self.stdout.write(f'🔄 Usuario actualizado: {username}')
            else:
                # Crear nuevo usuario
                password = user_data.pop('password')
                user = User.objects.create(**user_data)
                user.set_password(password)  # Django hashea automáticamente la contraseña
                user.save()
                self.stdout.write(f'✅ Usuario creado: {username}')

            created_users.append(user)

        # Asignar usuarios a grupos
        self.assign_users_to_groups(created_users)

        self.stdout.write(
            self.style.SUCCESS(f'👥 {len(created_users)} usuarios esenciales de desarrollo configurados')
        )

    def create_user_groups(self):
        """Crea los grupos de usuarios necesarios"""
        from django.contrib.contenttypes.models import ContentType
        from CaosNewsApp.models import Noticia

        # Obtener content type para el modelo Noticia
        noticia_content_type = ContentType.objects.get_for_model(Noticia)

        # Definir grupos y permisos
        groups_config = {
            'Administrador': {
                'permissions': ['add_noticia', 'change_noticia', 'view_noticia', 'delete_noticia']
            },
            'Periodista': {
                'permissions': ['add_noticia', 'change_noticia', 'view_noticia']
            },
            'Editor': {
                'permissions': ['add_noticia', 'change_noticia', 'view_noticia', 'delete_noticia']
            },
            'Usuario': {
                'permissions': ['view_noticia']
            }
        }

        for group_name, config in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                self.stdout.write(f'✅ Grupo creado: {group_name}')
            else:
                self.stdout.write(f'🔄 Grupo existe: {group_name}')

            # Limpiar permisos existentes del grupo
            group.permissions.clear()

            # Agregar permisos al grupo
            for perm_codename in config['permissions']:
                try:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=noticia_content_type
                    )
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Permiso no encontrado: {perm_codename}')
                    )

        self.stdout.write('✅ Grupos y permisos configurados')

    def assign_users_to_groups(self, created_users):
        """Asigna usuarios a sus grupos correspondientes"""

        # Mapeo de usuarios a grupos para desarrollo
        user_group_mapping = {
            'devadmin': 'Administrador',
            'devperiodista': 'Periodista',
            'devuser': 'Usuario',
        }

        for user in created_users:
            group_name = user_group_mapping.get(user.username)
            if group_name:
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.clear()  # Limpiar grupos existentes
                    user.groups.add(group)
                    user.save()
                    self.stdout.write(f'✅ Usuario {user.username} asignado al grupo {group_name}')
                except Group.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Grupo no encontrado: {group_name} para usuario {user.username}')
                    )

    def create_directories(self):
        """Crea directorios necesarios para desarrollo"""
        base_dir = Path(settings.BASE_DIR)

        directories = [
            base_dir / 'dev_emails',  # Para emails de desarrollo
            base_dir / 'media_dev' / 'news',  # Para imágenes de noticias
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        self.stdout.write('📁 Directorios de desarrollo creados')

    def display_dev_users_info(self):
        """Muestra información de los usuarios de desarrollo creados"""
        from CaosNewsApp.models import Noticia, Categoria, Pais
        User = get_user_model()

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🔧 ENTORNO DE DESARROLLO CONFIGURADO'))
        self.stdout.write('='*60)

        # Mostrar resumen de datos
        self.stdout.write('\n📊 Resumen de datos disponibles:')
        self.stdout.write(f'   👥 Usuarios: {User.objects.count()}')
        self.stdout.write(f'   📰 Noticias: {Noticia.objects.count()}')
        self.stdout.write(f'   📂 Categorías: {Categoria.objects.count()}')
        self.stdout.write(f'   🌍 Países: {Pais.objects.count()}')

        # Mostrar usuarios esenciales de desarrollo
        self.stdout.write('\n👥 USUARIOS DE DESARROLLO:')

        dev_users_info = [
            ('🔧 Administrador DEV', 'devadmin', 'devpass123', 'Acceso completo al sistema de desarrollo'),
            ('👤 Usuario DEV', 'devuser', 'devuser123', 'Usuario normal para pruebas'),
            ('📰 Periodista DEV', 'devperiodista', 'devper123', 'Crear y editar noticias'),
        ]

        for role, username, password, description in dev_users_info:
            self.stdout.write(f'\n{role}')
            self.stdout.write(f'  Usuario: {username}')
            self.stdout.write(f'  Contraseña: {password}')
            self.stdout.write(f'  Descripción: {description}')

        self.stdout.write('\n' + '='*60)
        self.stdout.write('🌐 URL Admin: http://127.0.0.1:8000/adminDJango/')
        self.stdout.write('🌐 URL Sitio: http://127.0.0.1:8000/')
        self.stdout.write('ℹ️  Base de datos: db_dev.sqlite3 (clonada de producción)')
        self.stdout.write('ℹ️  Media: media_dev/ (copiada de producción)')
        self.stdout.write('='*60 + '\n')

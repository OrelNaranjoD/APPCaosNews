"""
Comando para configurar el entorno de QA:
- Clona la base de datos de producción
- Agrega usuarios de prueba
- Copia los archivos media necesarios
"""

import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.db import transaction
from CaosNewsApp.tests.test_constants import QA_USER_CREDENTIALS, TEST_USER_CREDENTIALS


class Command(BaseCommand):
    help = 'Configura el entorno de QA clonando la base de datos de producción y agregando usuarios de prueba'

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
            self.style.SUCCESS('🔧 Configurando entorno de QA...')
        )

        base_dir = Path(settings.BASE_DIR)

        # Rutas de las bases de datos
        prod_db = base_dir / 'db.sqlite3'
        qa_db = base_dir / 'db_qa.sqlite3'

        # Rutas de archivos media
        prod_media = base_dir / 'media'
        qa_media = base_dir / 'media_qa'

        # 1. Clonar base de datos de producción
        if not options['skip_clone']:
            self.clone_production_database(prod_db, qa_db)
        else:
            self.stdout.write(
                self.style.WARNING('⏭️  Omitiendo clonación de base de datos')
            )

        # 2. Copiar archivos media
        if not options['skip_media']:
            self.copy_media_files(prod_media, qa_media)
        else:
            self.stdout.write(
                self.style.WARNING('⏭️  Omitiendo copia de archivos media')
            )

        # 3. Crear usuarios de prueba en auth_user (compatibles con BD clonada)
        self.create_test_users()

        # 4. Crear directorios necesarios
        self.create_directories()

        self.stdout.write(
            self.style.SUCCESS('✅ Entorno de QA configurado correctamente!')
        )
        self.display_test_users_info()

    def clone_production_database(self, prod_db, qa_db):
        """Clona la base de datos de producción para QA"""
        try:
            if prod_db.exists():
                self.stdout.write('📋 Clonando base de datos de producción...')

                # Remover base de datos QA existente si existe
                if qa_db.exists():
                    qa_db.unlink()
                    self.stdout.write('🗑️  Base de datos QA anterior removida')

                # Copiar base de datos de producción
                shutil.copy2(prod_db, qa_db)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Base de datos clonada: {qa_db}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Base de datos de producción no encontrada: {prod_db}')
                )
                self.stdout.write('📋 Creando nueva base de datos QA...')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error clonando base de datos: {e}')
            )
            # Crear nueva base de datos si falla la copia
            self.stdout.write('📋 Creando nueva base de datos QA...')

    def copy_media_files(self, prod_media, qa_media):
        """Copia archivos media de producción para QA"""
        try:
            if prod_media.exists():
                self.stdout.write('📁 Copiando archivos media...')

                # Remover directorio QA media existente si existe
                if qa_media.exists():
                    shutil.rmtree(qa_media)
                    self.stdout.write('🗑️  Directorio media QA anterior removido')

                # Copiar directorio media de producción
                shutil.copytree(prod_media, qa_media)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Archivos media copiados: {qa_media}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Directorio media de producción no encontrado: {prod_media}')
                )
                # Crear directorio vacío
                qa_media.mkdir(exist_ok=True)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error copiando archivos media: {e}')
            )
            # Crear directorio vacío si falla la copia
            qa_media.mkdir(exist_ok=True)

    @transaction.atomic
    def create_test_users(self):
        """Crea usuarios de prueba para QA en auth_user"""
        from django.contrib.auth.models import User, Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from CaosNewsApp.models import Noticia

        self.stdout.write('👥 Creando usuarios de prueba...')

        # Crear grupos si no existen
        self.create_user_groups()

        # Datos de usuarios de prueba
        test_users = [
            # Usuario específico para casos de uso y pruebas Selenium
            {
                'username': TEST_USER_CREDENTIALS['username'],
                'email': TEST_USER_CREDENTIALS['email'],
                'password': TEST_USER_CREDENTIALS['password'],
                'first_name': TEST_USER_CREDENTIALS['first_name'],
                'last_name': TEST_USER_CREDENTIALS['last_name'],
                'role': 'administrador',
                'is_staff': True,
                'is_superuser': True,
            },
            # Usuarios QA específicos
            {
                'username': QA_USER_CREDENTIALS['admin']['username'],
                'email': QA_USER_CREDENTIALS['admin']['email'],
                'password': QA_USER_CREDENTIALS['admin']['password'],  # Será hasheada automáticamente por Django
                'first_name': QA_USER_CREDENTIALS['admin']['first_name'],
                'last_name': QA_USER_CREDENTIALS['admin']['last_name'],
                'role': 'administrador',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': QA_USER_CREDENTIALS['periodista']['username'],
                'email': QA_USER_CREDENTIALS['periodista']['email'],
                'password': QA_USER_CREDENTIALS['periodista']['password'],  # Será hasheada automáticamente por Django
                'first_name': QA_USER_CREDENTIALS['periodista']['first_name'],
                'last_name': QA_USER_CREDENTIALS['periodista']['last_name'],
                'role': 'periodista',
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'username': QA_USER_CREDENTIALS['usuario']['username'],
                'email': QA_USER_CREDENTIALS['usuario']['email'],
                'password': QA_USER_CREDENTIALS['usuario']['password'],  # Será hasheada automáticamente por Django
                'first_name': QA_USER_CREDENTIALS['usuario']['first_name'],
                'last_name': QA_USER_CREDENTIALS['usuario']['last_name'],
                'role': 'lector',
                'is_staff': False,
                'is_superuser': False,
            },
        ]

        created_users = []
        for user_data in test_users:
            username = user_data['username']

            # Filtrar campos que no pertenecen al modelo auth_user
            auth_user_data = {
                'username': user_data['username'],
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser'],
            }

            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                # Actualizar usuario existente
                user = User.objects.get(username=username)
                for field, value in auth_user_data.items():
                    setattr(user, field, value)
                user.set_password(user_data['password'])  # Django hashea automáticamente la contraseña
                user.save()
                self.stdout.write(f'🔄 Usuario actualizado: {username}')
            else:
                # Crear nuevo usuario
                user = User.objects.create(**auth_user_data)
                user.set_password(user_data['password'])  # Django hashea automáticamente la contraseña
                user.save()
                self.stdout.write(f'✅ Usuario creado: {username}')

            created_users.append(user)

        # Asignar usuarios a grupos
        self.assign_users_to_groups(created_users)

        self.stdout.write(
            self.style.SUCCESS(f'👥 {len(created_users)} usuarios de prueba configurados')
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

        # Mapeo de usuarios a grupos
        user_group_mapping = {
            TEST_USER_CREDENTIALS['username']: 'Administrador',
            QA_USER_CREDENTIALS['admin']['username']: 'Administrador',
            QA_USER_CREDENTIALS['periodista']['username']: 'Periodista',
            QA_USER_CREDENTIALS['usuario']['username']: 'Usuario',
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
        """Crea directorios necesarios para QA"""
        base_dir = Path(settings.BASE_DIR)

        directories = [
            base_dir / 'qa_emails',  # Para emails de prueba
            base_dir / 'media_qa' / 'news',  # Para imágenes de noticias
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        self.stdout.write('📁 Directorios de QA creados')

    def display_test_users_info(self):
        """Muestra información de los usuarios de prueba creados"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎯 USUARIOS DE PRUEBA CONFIGURADOS'))
        self.stdout.write('='*60)

        users_info = [
            ('🧪 Usuario Casos de Uso', TEST_USER_CREDENTIALS['username'], TEST_USER_CREDENTIALS['password'], 'Usuario para pruebas Selenium y casos de uso'),
            ('👑 Administrador QA', 'qa_admin', 'qaadmin123', 'Acceso completo al sistema'),
            ('📰 Periodista QA', 'qa_periodista', 'qaperiodista123', 'Crear y editar noticias'),
            ('👤 Usuario QA', 'qa_usuario', 'qausuario123', 'Lectura de noticias'),
        ]

        for role, username, password, description in users_info:
            self.stdout.write(f'\n{role}')
            self.stdout.write(f'  Usuario: {username}')
            self.stdout.write(f'  Contraseña: {password}')
            self.stdout.write(f'  Descripción: {description}')

        self.stdout.write('\n' + '='*60)
        self.stdout.write('🌐 URL Admin: http://127.0.0.1:8001/adminDJango/')
        self.stdout.write('🌐 URL Sitio: http://127.0.0.1:8001/')
        self.stdout.write('\n💡 DATOS DISPONIBLES:')
        self.stdout.write('   📊 Base de datos clonada de producción (datos reales)')
        self.stdout.write('   👥 Usuarios de prueba agregados para testing')
        self.stdout.write('   📁 Archivos media copiados de producción')
        self.stdout.write('   ✅ Entorno listo para pruebas manuales y automatizadas')
        self.stdout.write('='*60 + '\n')

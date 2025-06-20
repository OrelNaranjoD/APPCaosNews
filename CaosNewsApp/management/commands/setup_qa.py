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
from CaosNewsApp.tests.test_constants import QA_USER_CREDENTIALS, TEST_USER_CREDENTIALS, TEST_DATA, SUBSCRIPTION_TEST_DATA


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
        parser.add_argument(
            '--skip-data',
            action='store_true',
            help='Omite la creación de datos de prueba',
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
        if not options['skip_data']:
            self.create_test_users()
        else:
            self.stdout.write(
                self.style.WARNING('⏭️  Omitiendo creación de usuarios de prueba')
            )

        # 4. Crear directorios necesarios
        self.create_directories()

        self.stdout.write(
            self.style.SUCCESS('✅ Entorno de QA configurado correctamente!')
        )

        if not options['skip_data']:
            self.stdout.write('📋 Información de usuarios de prueba:')
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

        # 5. Crear noticias de prueba
        self.create_test_news()

        # 6. Crear planes y suscripciones de prueba
        self.create_test_subscriptions()

    def create_test_news(self):
        """Crea noticias de prueba para QA"""
        from django.utils import timezone
        from django.core.files.base import ContentFile
        from CaosNewsApp.models import Noticia, Categoria, Pais, DetalleNoticia, ImagenNoticia
        from CaosNewsApp.tests.test_constants import TEST_DATA
        from django.contrib.auth.models import User
        import shutil
        from pathlib import Path

        self.stdout.write('📰 Creando noticias de prueba...')

        try:
            # 1. Obtener o crear categoría
            categoria, created = Categoria.objects.get_or_create(
                nombre_categoria=TEST_DATA['categoria_nombre']
            )
            if created:
                self.stdout.write(f'✅ Categoría creada: {categoria.nombre_categoria}')

            # 2. Obtener o crear país
            pais, created = Pais.objects.get_or_create(
                pais=TEST_DATA['pais_nombre']
            )
            if created:
                self.stdout.write(f'✅ País creado: {pais.pais}')

            # 3. Obtener usuario (ya creado en create_test_users)
            usuario = User.objects.get(username=TEST_DATA['usuario_autor'])

            # 4. Verificar si la noticia ya existe
            if not Noticia.objects.filter(titulo_noticia=TEST_DATA['titulo_noticia']).exists():
                # 5. Crear la noticia
                noticia = Noticia.objects.create(
                    titulo_noticia=TEST_DATA['titulo_noticia'],
                    cuerpo_noticia=TEST_DATA['cuerpo_noticia'],
                    id_categoria=categoria,
                    id_pais=pais,
                    id_usuario=usuario,
                    activo=True,
                    destacada=True,
                    eliminado=False
                )

                # 6. Crear referencia de imagen de prueba
                self.create_test_image(noticia)

                # 7. Aprobar y publicar la noticia automáticamente
                detalle = noticia.detalle
                detalle.estado = 'A'  # Aprobado
                detalle.publicada = True
                detalle.publicacion = timezone.now()
                detalle.save()

                self.stdout.write(f'✅ Noticia de prueba creada: {noticia.titulo_noticia}')
                self.stdout.write(f'📰 ID: {noticia.id_noticia} - Estado: Aprobada y publicada')
            else:
                self.stdout.write(f'📋 Noticia de prueba ya existe: {TEST_DATA["titulo_noticia"]}')

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Error creando noticia de prueba: {e}')
            )

    def create_test_image(self, noticia):
        """Crea referencia de imagen de prueba para la noticia"""
        from CaosNewsApp.models import ImagenNoticia
        from CaosNewsApp.tests.test_constants import TEST_DATA

        try:
            # Crear registro de imagen en la base de datos
            # La imagen ya fue copiada por copy_media_files()
            imagen_path = f'news/{TEST_DATA["imagen_nombre"]}'

            imagen_noticia = ImagenNoticia.objects.create(
                noticia=noticia
            )

            # Asignar la imagen usando la ruta desde TEST_DATA
            imagen_noticia.imagen.name = imagen_path
            imagen_noticia.save()

            self.stdout.write(f'✅ Referencia de imagen creada: {imagen_path}')

        except Exception as e:
            self.stdout.write(f'⚠️  Error creando referencia de imagen: {e}')

    def create_test_subscriptions(self):
        """Crea suscripción de prueba usando un plan estándar del sistema"""
        from django.utils import timezone
        from datetime import timedelta
        from CaosNewsApp.models import Plan, Suscripcion, PrecioPlan
        from django.contrib.auth.models import User

        self.stdout.write('💳 Creando suscripción de prueba con plan estándar...')

        try:
            # 1. Buscar plan estándar del sistema (Plan Premium o cualquier plan existente)
            suscripcion_data = SUBSCRIPTION_TEST_DATA['suscripcion_proxima_a_vencer']
            
            plan = Plan.objects.filter(nombre=suscripcion_data['plan'], activo=True).first()
            if not plan:
                # Si no existe Plan Premium, usar cualquier plan activo
                plan = Plan.objects.filter(activo=True).first()
                if not plan:
                    self.stdout.write('⚠️  No hay planes disponibles en el sistema')
                    return
                self.stdout.write(f'📋 Usando plan disponible: {plan.nombre}')

            # 2. Buscar precio estándar (Mensual o cualquier precio disponible)
            precio_plan = PrecioPlan.objects.filter(
                plan=plan,
                nombre_periodo=suscripcion_data['precio_periodo'],
                activo=True
            ).first()
            
            if not precio_plan:
                # Si no existe precio Mensual, usar cualquier precio disponible
                precio_plan = PrecioPlan.objects.filter(plan=plan, activo=True).first()
                if not precio_plan:
                    self.stdout.write(f'⚠️  No hay precios disponibles para el plan {plan.nombre}')
                    return
                self.stdout.write(f'📋 Usando precio disponible: {precio_plan.nombre_periodo}')

            # 3. Buscar usuario de prueba
            try:
                usuario = User.objects.get(username=suscripcion_data['usuario'])
            except User.DoesNotExist:
                self.stdout.write(f'⚠️  Usuario {suscripcion_data["usuario"]} no existe')
                return

            # 4. Verificar si ya existe una suscripción activa para este usuario
            suscripcion_existente = Suscripcion.objects.filter(
                usuario=usuario,
                estado='A'
            ).first()

            if suscripcion_existente:
                # Actualizar suscripción existente para que expire en 1 día
                ahora = timezone.now()
                dias_restantes = suscripcion_data['dias_restantes']
                nueva_fecha_fin = ahora + timedelta(days=dias_restantes)
                
                suscripcion_existente.fecha_fin = nueva_fecha_fin
                suscripcion_existente.save()
                
                self.stdout.write('✅ Suscripción existente actualizada:')
                self.stdout.write(f'   Usuario: {usuario.username}')
                self.stdout.write(f'   Plan: {suscripcion_existente.plan.nombre}')
                self.stdout.write(f'   Nueva fecha fin: {nueva_fecha_fin.strftime("%Y-%m-%d %H:%M")}')
                self.stdout.write(f'   Días restantes: {suscripcion_existente.dias_restantes}')
                self.stdout.write(f'   Próxima a vencer: {"Sí" if suscripcion_existente.esta_proxima_a_vencer else "No"}')
            else:
                # Crear nueva suscripción que expire en 1 día
                ahora = timezone.now()
                dias_restantes = suscripcion_data['dias_restantes']
                fecha_inicio = ahora - timedelta(days=precio_plan.duracion_dias - dias_restantes)
                fecha_fin = ahora + timedelta(days=dias_restantes)

                suscripcion = Suscripcion.objects.create(
                    usuario=usuario,
                    plan=plan,
                    precio_plan=precio_plan,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    estado=suscripcion_data['estado']
                )

                self.stdout.write('✅ Suscripción de prueba creada:')
                self.stdout.write(f'   Usuario: {usuario.username}')
                self.stdout.write(f'   Plan: {plan.nombre}')
                self.stdout.write(f'   Período: {precio_plan.nombre_periodo}')
                self.stdout.write(f'   Precio: ${precio_plan.valor}')
                self.stdout.write(f'   Fecha inicio: {fecha_inicio.strftime("%Y-%m-%d %H:%M")}')
                self.stdout.write(f'   Fecha fin: {fecha_fin.strftime("%Y-%m-%d %H:%M")}')
                self.stdout.write(f'   Días restantes: {suscripcion.dias_restantes}')
                self.stdout.write(f'   Próxima a vencer: {"Sí" if suscripcion.esta_proxima_a_vencer else "No"}')

        except Exception as e:
            self.stdout.write(f'⚠️  Error creando suscripción de prueba: {e}')
            import traceback
            traceback.print_exc()

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
        self.stdout.write('   📊 Base de datos clonada de producción (datos reales + planes básicos)')
        self.stdout.write('   👥 Usuarios de prueba agregados para testing')
        self.stdout.write('   📁 Archivos media copiados de producción')
        self.stdout.write('   📰 Noticias de prueba creadas y publicadas')
        self.stdout.write('   💳 Plan especial QA y suscripción próxima a vencer (1 día)')
        self.stdout.write('   ✅ Entorno listo para pruebas manuales y automatizadas')
        self.stdout.write('='*60 + '\n')

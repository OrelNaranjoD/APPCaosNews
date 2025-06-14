"""
Comando para crear noticias de prueba en el entorno QA
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from CaosNewsApp.models import Noticia, Categoria, Pais, DetalleNoticia
from CaosNewsApp.tests.test_constants import TEST_DATA, QA_USER_CREDENTIALS, TEST_USER_CREDENTIALS

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea noticias de prueba para el entorno QA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Elimina las noticias de prueba existentes antes de crear nuevas',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('📰 Creando noticias de prueba...')
        )

        # Eliminar noticias existentes si se solicita
        if options['delete_existing']:
            self.delete_existing_test_news()

        # Crear noticias de prueba
        self.create_test_news()

        self.stdout.write(
            self.style.SUCCESS('✅ Noticias de prueba creadas correctamente!')
        )

    def delete_existing_test_news(self):
        """Elimina las noticias de prueba existentes"""
        test_title = TEST_DATA['titulo_noticia']
        existing_news = Noticia.objects.filter(titulo_noticia=test_title)
        count = existing_news.count()

        if count > 0:
            existing_news.delete()
            self.stdout.write(f'🗑️  {count} noticia(s) de prueba eliminada(s)')

    @transaction.atomic
    def create_test_news(self):
        """Crea las noticias de prueba"""
        try:
            # 1. Obtener o crear categoría
            categoria, created = Categoria.objects.get_or_create(
                nombre_categoria=TEST_DATA['categoria_nombre']
            )
            if created:
                self.stdout.write(f'✅ Categoría creada: {categoria.nombre_categoria}')
            else:
                self.stdout.write(f'📋 Categoría existente: {categoria.nombre_categoria}')

            # 2. Obtener o crear país
            pais, created = Pais.objects.get_or_create(
                pais=TEST_DATA['pais_nombre']
            )
            if created:
                self.stdout.write(f'✅ País creado: {pais.pais}')
            else:
                self.stdout.write(f'📋 País existente: {pais.pais}')

            # 3. Obtener o crear usuario periodista
            usuario, created = User.objects.get_or_create(
                username=TEST_DATA['usuario_autor'],
                defaults={
                    'email': TEST_USER_CREDENTIALS['email'],
                    'first_name': TEST_USER_CREDENTIALS['first_name'],
                    'last_name': TEST_USER_CREDENTIALS['last_name'],
                    'is_active': True,
                }
            )

            if created:
                usuario.set_password(TEST_USER_CREDENTIALS['password'])
                usuario.save()
                self.stdout.write(f'✅ Usuario creado: {usuario.username}')
            else:
                self.stdout.write(f'📋 Usuario existente: {usuario.username}')

            # 4. Verificar si la noticia ya existe
            if Noticia.objects.filter(titulo_noticia=TEST_DATA['titulo_noticia']).exists():
                self.stdout.write(
                    self.style.WARNING(f'⚠️  La noticia ya existe: {TEST_DATA["titulo_noticia"]}')
                )
                return

            # 5. Crear la noticia
            noticia = Noticia.objects.create(
                titulo_noticia=TEST_DATA['titulo_noticia'],
                cuerpo_noticia=TEST_DATA['cuerpo_noticia'],
                id_categoria=categoria,
                id_pais=pais,
                id_usuario=usuario,
                activo=True,
                destacada=True,  # Hacer que sea destacada para que sea visible
                eliminado=False
            )

            self.stdout.write(f'✅ Noticia creada: {noticia.titulo_noticia}')
            self.stdout.write(f'📅 ID: {noticia.id_noticia}')
            self.stdout.write(f'👤 Autor: {usuario.first_name} {usuario.last_name}')
            self.stdout.write(f'📂 Categoría: {categoria.nombre_categoria}')
            self.stdout.write(f'🌍 País: {pais.pais}')

            # 6. Verificar que se creó el detalle automáticamente
            try:
                detalle = DetalleNoticia.objects.get(noticia=noticia)
                # Aprobar y publicar la noticia
                detalle.estado = 'A'  # Aprobado
                detalle.publicada = True
                detalle.publicacion = timezone.now()
                detalle.save()

                self.stdout.write('✅ Detalle creado y aprobado automáticamente')

            except DetalleNoticia.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING('⚠️  No se creó el detalle automáticamente')
                )

            # 7. Mostrar información de la noticia creada
            self.display_news_info(noticia)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando noticia de prueba: {e}')
            )
            raise

    def display_news_info(self, noticia):
        """Muestra información de la noticia creada"""
        self.stdout.write('\n📰 Información de la noticia creada:')
        self.stdout.write(f'   Título: {noticia.titulo_noticia}')
        self.stdout.write(f'   ID: {noticia.id_noticia}')
        self.stdout.write(f'   Activa: {noticia.activo}')
        self.stdout.write(f'   Destacada: {noticia.destacada}')
        self.stdout.write(f'   Eliminada: {noticia.eliminado}')
        self.stdout.write(f'   Fecha creación: {noticia.fecha_creacion}')

        try:
            detalle = noticia.detalle
            self.stdout.write(f'   Estado: {detalle.get_estado_display() if detalle.estado else "Sin estado"}')
            self.stdout.write(f'   Publicada: {detalle.publicada}')
            self.stdout.write(f'   Fecha publicación: {detalle.publicacion}')
        except DetalleNoticia.DoesNotExist:
            self.stdout.write('   Detalle: No disponible')

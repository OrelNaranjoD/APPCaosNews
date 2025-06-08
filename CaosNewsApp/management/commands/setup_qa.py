from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Configura el entorno de QA reiniciando la base de datos y cargando datos de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-fixtures',
            action='store_true',
            help='No carga los fixtures automáticamente',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING('🧪 Configurando entorno de QA...')
        )

        # Resetear base de datos completamente
        self.stdout.write('⚠️ Reseteando base de datos de QA...')
        call_command('flush', '--noinput')

        # Aplicar migraciones
        self.stdout.write('📦 Aplicando migraciones...')
        call_command('migrate')

        # Cargar fixtures si no se especifica lo contrario
        if not options['no_fixtures']:
            self.stdout.write('📁 Cargando datos de prueba (fixtures)...')
            try:
                call_command('loaddata', 'test_data.json')
                self.stdout.write(
                    self.style.SUCCESS('✅ Fixtures cargados exitosamente')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error cargando fixtures: {e}')
                )

        # Crear superusuario de QA
        self.stdout.write('👤 Creando superusuario de QA...')
        with transaction.atomic():
            if not User.objects.filter(username='testadmin').exists():
                User.objects.create_superuser(
                    username='testadmin',
                    email='testadmin@caosnews.com',
                    password='testpass123',
                    first_name='Test',
                    last_name='Admin'
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ Superusuario de QA creado: testadmin/testpass123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('ℹ️ Superusuario de QA ya existe')
                )

        # Mostrar resumen de datos
        self._show_data_summary()

        self.stdout.write(
            self.style.SUCCESS('\n🎯 Entorno de QA configurado exitosamente!')
        )
        self.stdout.write(
            self.style.HTTP_INFO('\n📍 Servidor QA ejecutándose en: http://127.0.0.1:8001')
        )
        self.stdout.write(
            self.style.HTTP_INFO('🔑 Panel admin: http://127.0.0.1:8001/adminDJango/ (testadmin/testpass123)')
        )

    def _show_data_summary(self):
        """Muestra un resumen de los datos disponibles"""
        from CaosNewsApp.models import Noticia, Categoria, Pais

        self.stdout.write('\n📊 Resumen de datos en QA:')
        self.stdout.write(f'   👥 Usuarios: {User.objects.count()}')
        self.stdout.write(f'   📰 Noticias: {Noticia.objects.count()}')
        self.stdout.write(f'   📂 Categorías: {Categoria.objects.count()}')
        self.stdout.write(f'   🌍 Países: {Pais.objects.count()}')

        self.stdout.write('\n👤 Usuarios de prueba disponibles:')

        # Mostrar usuarios de fixtures
        test_users = User.objects.filter(username__in=['testuser', 'admin'])
        for user in test_users:
            role = "superusuario" if user.is_superuser else "usuario normal"
            self.stdout.write(f'   - {user.username} ({user.email}) - {role}')

        # Mostrar superusuario de QA
        if User.objects.filter(username='testadmin').exists():
            self.stdout.write('   - testadmin (testadmin@caosnews.com) - superusuario de QA')

        self.stdout.write('\n💡 Base de datos reseteada completamente en cada ejecución')
        self.stdout.write('💡 Datos de fixtures recargados automáticamente')

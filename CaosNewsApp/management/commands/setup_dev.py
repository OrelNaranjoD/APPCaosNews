from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Configura el entorno de desarrollo con datos de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Resetea la base de datos antes de cargar los datos',
        )
        parser.add_argument(
            '--no-fixtures',
            action='store_true',
            help='No carga los fixtures automáticamente',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING('🔧 Configurando entorno de desarrollo...')
        )

        # Resetear base de datos si se solicita
        if options['reset']:
            self.stdout.write('⚠️ Reseteando base de datos...')
            call_command('flush', '--noinput')
            call_command('migrate')

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

        # Crear superusuario de desarrollo
        self.stdout.write('👤 Verificando superusuario de desarrollo...')
        with transaction.atomic():
            if not User.objects.filter(username='devadmin').exists():
                User.objects.create_superuser(
                    username='devadmin',
                    email='devadmin@caosnews.com',
                    password='devpass123',
                    first_name='Dev',
                    last_name='Admin'
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ Superusuario de desarrollo creado: devadmin/devpass123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('ℹ️ Superusuario de desarrollo ya existe')
                )

        # Mostrar resumen de datos
        self._show_data_summary()

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Entorno de desarrollo configurado exitosamente!')
        )

    def _show_data_summary(self):
        """Muestra un resumen de los datos disponibles"""
        from CaosNewsApp.models import Noticia, Categoria, Pais

        self.stdout.write('\n📊 Resumen de datos disponibles:')
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

        # Mostrar superusuario de desarrollo
        if User.objects.filter(username='devadmin').exists():
            self.stdout.write('   - devadmin (devadmin@caosnews.com) - superusuario de desarrollo')

        self.stdout.write('\n💡 Para usar contraseñas de fixtures, revisa el archivo test_data.json')
        self.stdout.write('💡 Superusuario de desarrollo: devadmin/devpass123')

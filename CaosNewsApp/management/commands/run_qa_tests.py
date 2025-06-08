"""
Comando para ejecutar pruebas pytest en el entorno de QA
"""

import subprocess
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Ejecuta pruebas pytest en el entorno de QA con la base de datos clonada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Ejecuta las pruebas en modo verbose',
        )
        parser.add_argument(
            '--coverage',
            '-c',
            action='store_true',
            help='Ejecuta las pruebas con coverage',
        )
        parser.add_argument(
            '--test-path',
            '-p',
            type=str,
            help='Ruta específica de pruebas a ejecutar',
            default='CaosNewsApp/tests/',
        )
        parser.add_argument(
            '--markers',
            '-m',
            type=str,
            help='Ejecutar pruebas con marcadores específicos (ej: -m "not slow")',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧪 Ejecutando pruebas pytest en entorno QA...')
        )

        # Verificar que estamos en modo QA
        if not self.verify_qa_environment():
            return

        # Construir comando pytest
        pytest_cmd = self.build_pytest_command(options)

        # Mostrar información previa
        self.show_test_info(pytest_cmd)

        # Ejecutar pruebas
        self.run_tests(pytest_cmd)

    def verify_qa_environment(self):
        """Verifica que estemos ejecutando en el entorno QA"""
        settings_module = settings.SETTINGS_MODULE

        if 'settings_qa' not in settings_module:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Este comando debe ejecutarse en el entorno QA.\n'
                    '   Use: $env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_qa"'
                )
            )
            return False

        # Verificar que existe la base de datos QA
        qa_db = Path(settings.BASE_DIR) / 'db_qa.sqlite3'
        if not qa_db.exists():
            self.stdout.write(
                self.style.ERROR(
                    '❌ Base de datos QA no encontrada.\n'
                    '   Ejecute primero: python manage.py setup_qa'
                )
            )
            return False

        self.stdout.write(
            self.style.SUCCESS('✅ Entorno QA verificado correctamente')
        )
        return True

    def build_pytest_command(self, options):
        """Construye el comando pytest con las opciones especificadas"""
        cmd = ['pytest']

        # Usar configuración unificada (pytest.ini)
        # Ya no necesitamos especificar -c porque pytest.ini es el default

        # Ruta de pruebas
        test_path = options['test_path']
        cmd.append(test_path)

        # Verbose (solo si no está en la config)
        if options['verbose']:
            cmd.append('-v')

        # Coverage (agregar solo si se solicita)
        if options['coverage']:
            cmd.extend([
                '--cov=CaosNewsApp',
                '--cov-report=html:htmlcov_qa',
                '--cov-report=term-missing',
                '--cov-report=xml'
            ])

        # Marcadores
        if options['markers']:
            cmd.extend(['-m', options['markers']])

        return cmd

    def show_test_info(self, pytest_cmd):
        """Muestra información sobre las pruebas que se van a ejecutar"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('🎯 INFORMACIÓN DE PRUEBAS QA UNIFICADAS'))
        self.stdout.write('='*60)

        self.stdout.write('⚠️  IMPORTANTE: El servidor QA debe estar ejecutándose en http://127.0.0.1:8001')
        self.stdout.write('   Ejecutar primero: .\\scripts\\run_qa_server.ps1')
        self.stdout.write('')
        self.stdout.write(f'📁 Base de datos: db_qa.sqlite3 (clonada de producción)')
        self.stdout.write(f'🌐 Configuración: {settings.SETTINGS_MODULE}')
        self.stdout.write('🧪 Comando pytest: ' + " ".join(pytest_cmd))
        self.stdout.write('📂 Directorio media: media_qa/')
        self.stdout.write('📊 Coverage: Automático (htmlcov_qa/)')

        # Mostrar usuarios de prueba disponibles
        self.stdout.write('\n👥 Usuarios de prueba disponibles:')
        self.stdout.write('   • qa_admin / qaadmin123 (Administrador)')
        self.stdout.write('   • qa_periodista / qaperiodista123 (Periodista)')
        self.stdout.write('   • qa_usuario / qausuario123 (Usuario normal)')

        self.stdout.write('\n💡 Configuración unificada: pytest.ini (único archivo)')
        self.stdout.write('💡 Las pruebas Selenium usan servidor QA externo en puerto 8001')
        self.stdout.write('💡 Las pruebas unitarias usan datos reales clonados de producción')
        self.stdout.write('='*60 + '\n')

    def run_tests(self, pytest_cmd):
        """Ejecuta las pruebas pytest"""
        try:
            self.stdout.write(
                self.style.HTTP_INFO('🚀 Iniciando ejecución de pruebas...\n')
            )

            # Ejecutar pytest
            result = subprocess.run(
                pytest_cmd,
                cwd=settings.BASE_DIR,
                capture_output=False,  # Mostrar output en tiempo real
                text=True
            )

            # Mostrar resultado
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS('\n✅ Todas las pruebas pasaron exitosamente!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ Algunas pruebas fallaron (código: {result.returncode})')
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    '❌ pytest no encontrado. Instale pytest:\n'
                    '   pip install pytest pytest-django pytest-cov'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error ejecutando pruebas: {e}')
            )

    def post_test_summary(self):
        """Muestra resumen post-ejecución"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('📊 RESUMEN POST-PRUEBAS QA'))
        self.stdout.write('='*60)

        coverage_dir = Path(settings.BASE_DIR) / 'htmlcov_qa'
        if coverage_dir.exists():
            self.stdout.write('📈 Reporte de coverage generado en: htmlcov_qa/index.html')

        self.stdout.write('📋 Para reiniciar el entorno QA: python manage.py setup_qa')
        self.stdout.write('🔄 Para ejecutar servidor QA: scripts\\run_qa_server.ps1')
        self.stdout.write('⚙️  Configuración unificada en: pytest.ini')
        self.stdout.write('='*60)

"""
Comando para limpiar el entorno de desarrollo
Elimina datos de desarrollo y archivos temporales
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from pathlib import Path

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Limpia el entorno de desarrollo eliminando datos de prueba y archivos temporales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            action='store_true',
            help='Elimina la base de datos de desarrollo'
        )
        parser.add_argument(
            '--media',
            action='store_true',
            help='Elimina archivos media de desarrollo'
        )
        parser.add_argument(
            '--logs',
            action='store_true',
            help='Elimina archivos de log de desarrollo'
        )
        parser.add_argument(
            '--emails',
            action='store_true',
            help='Elimina archivos de email de desarrollo'
        )
        parser.add_argument(
            '--cache',
            action='store_true',
            help='Limpia caché de desarrollo'
        )
        parser.add_argument(
            '--python-cache',
            action='store_true',
            help='Elimina archivos __pycache__ y *.pyc'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Limpia todo (equivale a --database --media --logs --emails --cache --python-cache)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='No pide confirmación'
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)

        if options['all']:
            options['database'] = True
            options['media'] = True
            options['logs'] = True
            options['emails'] = True
            options['cache'] = True
            options['python_cache'] = True

        # Lista de operaciones a realizar
        operations = []
        if options['database']:
            operations.append("🗄️ Base de datos de desarrollo")
        if options['media']:
            operations.append("📁 Archivos media de desarrollo")
        if options['logs']:
            operations.append("📋 Archivos de log")
        if options['emails']:
            operations.append("📧 Archivos de email")
        if options['cache']:
            operations.append("💾 Caché")
        if options['python_cache']:
            operations.append("🐍 Cache de Python (__pycache__, *.pyc)")

        if not operations:
            self.stdout.write(
                self.style.WARNING("⚠️ No se especificaron operaciones de limpieza")
            )
            self.stdout.write("Usa --help para ver las opciones disponibles")
            return

        # Mostrar resumen
        self.stdout.write("🧹 Operaciones de limpieza de desarrollo a realizar:")
        for op in operations:
            self.stdout.write(f"  • {op}")

        # Confirmación
        if not options['force']:
            confirm = input("\n¿Continuar? (s/N): ")
            if confirm.lower() not in ['s', 'sí', 'si', 'yes', 'y']:
                self.stdout.write("❌ Operación cancelada")
                return

        # Ejecutar operaciones
        self.stdout.write("\n🧹 Iniciando limpieza del entorno de desarrollo...")

        if options['database']:
            self.clean_database(base_dir)

        if options['media']:
            self.clean_media(base_dir)

        if options['logs']:
            self.clean_logs(base_dir)

        if options['emails']:
            self.clean_emails(base_dir)

        if options['cache']:
            self.clean_cache()

        if options['python_cache']:
            self.clean_python_cache(base_dir)

        self.stdout.write(
            self.style.SUCCESS('\n✅ Limpieza del entorno de desarrollo completada exitosamente')
        )

    def clean_database(self, base_dir):
        """Elimina la base de datos de desarrollo"""
        dev_db = base_dir / "db_dev.sqlite3"
        dev_db_journal = base_dir / "db_dev.sqlite3-journal"

        if dev_db.exists():
            self.stdout.write("🗄️ Eliminando base de datos de desarrollo...")
            dev_db.unlink()
            self.stdout.write(
                self.style.SUCCESS("✅ Base de datos de desarrollo eliminada")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ Base de datos de desarrollo no encontrada")
            )

        if dev_db_journal.exists():
            dev_db_journal.unlink()
            self.stdout.write(
                self.style.SUCCESS("✅ Journal de base de datos eliminado")
            )

    def clean_media(self, base_dir):
        """Elimina archivos media de desarrollo"""
        media_dev = base_dir / "media_dev"

        if media_dev.exists():
            self.stdout.write("📁 Eliminando archivos media de desarrollo...")
            shutil.rmtree(media_dev)
            self.stdout.write(
                self.style.SUCCESS("✅ Archivos media de desarrollo eliminados")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ Directorio media_dev no encontrado")
            )

    def clean_logs(self, base_dir):
        """Elimina archivos de log de desarrollo"""
        log_files = [
            base_dir / "dev_debug.log",
            base_dir / "dev_debug.log.1",
            base_dir / "dev_debug.log.2",
        ]

        cleaned = 0
        for log_file in log_files:
            if log_file.exists():
                log_file.unlink()
                cleaned += 1

        if cleaned > 0:
            self.stdout.write(f"📋 Eliminados {cleaned} archivos de log")
            self.stdout.write(
                self.style.SUCCESS("✅ Archivos de log limpiados")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ No se encontraron archivos de log")
            )

    def clean_emails(self, base_dir):
        """Elimina archivos de email de desarrollo"""
        dev_emails = base_dir / "dev_emails"

        if dev_emails.exists():
            self.stdout.write("📧 Eliminando archivos de email de desarrollo...")
            shutil.rmtree(dev_emails)
            self.stdout.write(
                self.style.SUCCESS("✅ Archivos de email de desarrollo eliminados")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ Directorio dev_emails no encontrado")
            )

    def clean_cache(self):
        """Limpia caché de desarrollo"""
        from django.core.cache import cache

        self.stdout.write("💾 Limpiando caché...")
        cache.clear()
        self.stdout.write(
            self.style.SUCCESS("✅ Caché limpiado")
        )

    def clean_python_cache(self, base_dir):
        """Elimina archivos __pycache__ y *.pyc"""
        self.stdout.write("🐍 Limpiando cache de Python...")

        # Contar archivos antes de eliminar
        pyc_count = 0
        cache_dirs = 0

        # Buscar y eliminar archivos .pyc
        for pyc_file in base_dir.rglob("*.pyc"):
            try:
                pyc_file.unlink()
                pyc_count += 1
            except OSError:
                pass  # Ignorar errores de permisos

        # Buscar y eliminar directorios __pycache__
        for cache_dir in base_dir.rglob("__pycache__"):
            try:
                shutil.rmtree(cache_dir)
                cache_dirs += 1
            except OSError:
                pass  # Ignorar errores de permisos

        # También limpiar archivos de cobertura y pytest
        coverage_files = [
            base_dir / ".coverage",
            base_dir / "htmlcov_dev",
            base_dir / ".pytest_cache"
        ]

        coverage_cleaned = 0
        for coverage_file in coverage_files:
            if coverage_file.exists():
                try:
                    if coverage_file.is_dir():
                        shutil.rmtree(coverage_file)
                    else:
                        coverage_file.unlink()
                    coverage_cleaned += 1
                except OSError:
                    pass

        self.stdout.write(f"  • Eliminados {pyc_count} archivos .pyc")
        self.stdout.write(f"  • Eliminados {cache_dirs} directorios __pycache__")
        if coverage_cleaned > 0:
            self.stdout.write(f"  • Eliminados {coverage_cleaned} archivos de cobertura/testing")

        self.stdout.write(
            self.style.SUCCESS("✅ Cache de Python limpiado")
        )

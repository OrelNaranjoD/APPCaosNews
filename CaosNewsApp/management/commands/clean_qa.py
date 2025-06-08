"""
Comando para limpiar el entorno de QA
Elimina datos de prueba y archivos temporales
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from pathlib import Path

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Limpia el entorno de QA eliminando datos de prueba y archivos temporales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            action='store_true',
            help='Elimina la base de datos de QA'
        )
        parser.add_argument(
            '--media',
            action='store_true',
            help='Elimina archivos media de QA'
        )
        parser.add_argument(
            '--logs',
            action='store_true',
            help='Elimina archivos de log de QA'
        )
        parser.add_argument(
            '--emails',
            action='store_true',
            help='Elimina archivos de email de QA'
        )
        parser.add_argument(
            '--cache',
            action='store_true',
            help='Limpia caché de QA'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Limpia todo (equivale a --database --media --logs --emails --cache)'
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

        # Lista de operaciones a realizar
        operations = []
        if options['database']:
            operations.append("🗄️ Base de datos QA")
        if options['media']:
            operations.append("📁 Archivos media QA")
        if options['logs']:
            operations.append("📋 Archivos de log")
        if options['emails']:
            operations.append("📧 Archivos de email")
        if options['cache']:
            operations.append("💾 Caché")

        if not operations:
            self.stdout.write(
                self.style.WARNING("⚠️ No se especificaron operaciones de limpieza")
            )
            self.stdout.write("Usa --help para ver las opciones disponibles")
            return

        # Mostrar resumen
        self.stdout.write("🧹 Operaciones de limpieza a realizar:")
        for op in operations:
            self.stdout.write(f"  • {op}")

        # Confirmación
        if not options['force']:
            confirm = input("\n¿Continuar? (s/N): ")
            if confirm.lower() not in ['s', 'sí', 'si', 'yes', 'y']:
                self.stdout.write("❌ Operación cancelada")
                return

        # Ejecutar operaciones
        self.stdout.write("\n🧹 Iniciando limpieza...")

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

        self.stdout.write(
            self.style.SUCCESS('\n✅ Limpieza de QA completada exitosamente')
        )

    def clean_database(self, base_dir):
        """Elimina la base de datos de QA"""
        qa_db = base_dir / "db_qa.sqlite3"

        if qa_db.exists():
            self.stdout.write("🗄️ Eliminando base de datos QA...")
            qa_db.unlink()
            self.stdout.write(
                self.style.SUCCESS("✅ Base de datos QA eliminada")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ Base de datos QA no encontrada")
            )

    def clean_media(self, base_dir):
        """Elimina archivos media de QA"""
        media_qa = base_dir / "media_qa"

        if media_qa.exists():
            self.stdout.write("📁 Eliminando archivos media QA...")
            shutil.rmtree(media_qa)
            self.stdout.write(
                self.style.SUCCESS("✅ Archivos media QA eliminados")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ Directorio media_qa no encontrado")
            )

    def clean_logs(self, base_dir):
        """Elimina archivos de log de QA"""
        log_files = [
            base_dir / "qa_debug.log",
            base_dir / "qa_debug.log.1",
            base_dir / "qa_debug.log.2",
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
        """Elimina archivos de email de QA"""
        qa_emails = base_dir / "qa_emails"

        if qa_emails.exists():
            self.stdout.write("📧 Eliminando archivos de email QA...")
            shutil.rmtree(qa_emails)
            self.stdout.write(
                self.style.SUCCESS("✅ Archivos de email QA eliminados")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ Directorio qa_emails no encontrado")
            )

    def clean_cache(self):
        """Limpia caché de QA"""
        from django.core.cache import cache

        self.stdout.write("💾 Limpiando caché...")
        cache.clear()
        self.stdout.write(
            self.style.SUCCESS("✅ Caché limpiado")
        )

"""
Comando para sincronizar archivos media entre entornos
Optimiza el uso de espacio usando enlaces duros o sincronización inteligente
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import stat


class Command(BaseCommand):
    help = 'Sincroniza archivos media entre entornos de forma eficiente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='media',
            help='Directorio fuente (por defecto: media)'
        )
        parser.add_argument(
            '--target',
            type=str,
            default='media_qa',
            help='Directorio destino (por defecto: media_qa)'
        )
        parser.add_argument(
            '--method',
            choices=['copy', 'hardlink', 'sync'],
            default='sync',
            help='Método de sincronización (copy/hardlink/sync)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la operación sin realizar cambios'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada'
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        source_dir = base_dir / options['source']
        target_dir = base_dir / options['target']

        if not source_dir.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ Directorio fuente no existe: {source_dir}")
            )
            return

        self.stdout.write(f"🔄 Sincronizando media:")
        self.stdout.write(f"   📂 Fuente: {source_dir}")
        self.stdout.write(f"   📂 Destino: {target_dir}")
        self.stdout.write(f"   🔧 Método: {options['method']}")

        if options['dry_run']:
            self.stdout.write("   🔍 Modo simulación (dry-run)")

        # Crear directorio destino si no existe
        if not options['dry_run']:
            target_dir.mkdir(exist_ok=True)

        if options['method'] == 'hardlink':
            self.sync_with_hardlinks(source_dir, target_dir, options)
        elif options['method'] == 'copy':
            self.sync_with_copy(source_dir, target_dir, options)
        else:  # sync
            self.sync_intelligent(source_dir, target_dir, options)

    def sync_with_hardlinks(self, source_dir, target_dir, options):
        """Sincroniza usando enlaces duros (ahorra espacio)"""
        self.stdout.write("🔗 Usando enlaces duros para ahorrar espacio...")

        synced = 0
        errors = 0

        for source_file in source_dir.rglob('*'):
            if source_file.is_file():
                relative_path = source_file.relative_to(source_dir)
                target_file = target_dir / relative_path

                try:
                    if not options['dry_run']:
                        # Crear directorio padre si no existe
                        target_file.parent.mkdir(parents=True, exist_ok=True)

                        # Eliminar archivo destino si existe
                        if target_file.exists():
                            target_file.unlink()

                        # Crear enlace duro
                        os.link(source_file, target_file)

                    synced += 1
                    if options['verbose']:
                        self.stdout.write(f"  🔗 {relative_path}")

                except OSError as e:
                    errors += 1
                    if options['verbose']:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠️ Error en {relative_path}: {e}")
                        )

        self.stdout.write(
            self.style.SUCCESS(f"✅ Sincronización completada: {synced} archivos, {errors} errores")
        )

    def sync_with_copy(self, source_dir, target_dir, options):
        """Sincroniza copiando archivos"""
        self.stdout.write("📋 Copiando archivos...")

        synced = 0

        for source_file in source_dir.rglob('*'):
            if source_file.is_file():
                relative_path = source_file.relative_to(source_dir)
                target_file = target_dir / relative_path

                if not options['dry_run']:
                    # Crear directorio padre si no existe
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    # Copiar archivo
                    shutil.copy2(source_file, target_file)

                synced += 1
                if options['verbose']:
                    self.stdout.write(f"  📋 {relative_path}")

        self.stdout.write(
            self.style.SUCCESS(f"✅ Copiados {synced} archivos")
        )

    def sync_intelligent(self, source_dir, target_dir, options):
        """Sincronización inteligente (solo archivos nuevos o modificados)"""
        self.stdout.write("🧠 Sincronización inteligente...")

        new_files = 0
        updated_files = 0
        unchanged_files = 0

        for source_file in source_dir.rglob('*'):
            if source_file.is_file():
                relative_path = source_file.relative_to(source_dir)
                target_file = target_dir / relative_path

                # Verificar si necesita sincronización
                needs_sync = False
                status = ""

                if not target_file.exists():
                    needs_sync = True
                    status = "NUEVO"
                    new_files += 1
                else:
                    # Comparar timestamp y tamaño
                    source_stat = source_file.stat()
                    target_stat = target_file.stat()

                    if (source_stat.st_mtime > target_stat.st_mtime or
                        source_stat.st_size != target_stat.st_size):
                        needs_sync = True
                        status = "MODIFICADO"
                        updated_files += 1
                    else:
                        unchanged_files += 1
                        if options['verbose']:
                            status = "SIN CAMBIOS"

                if needs_sync and not options['dry_run']:
                    # Crear directorio padre si no existe
                    target_file.parent.mkdir(parents=True, exist_ok=True)

                    # Intentar crear enlace duro primero, si falla copiar
                    try:
                        if target_file.exists():
                            target_file.unlink()
                        os.link(source_file, target_file)
                        method = "ENLACE"
                    except OSError:
                        shutil.copy2(source_file, target_file)
                        method = "COPIA"

                    if options['verbose']:
                        self.stdout.write(f"  🔄 {relative_path} ({status} - {method})")
                elif options['verbose'] and status:
                    self.stdout.write(f"  ℹ️ {relative_path} ({status})")

        # Resumen
        total_processed = new_files + updated_files + unchanged_files
        self.stdout.write(f"\n📊 Resumen de sincronización:")
        self.stdout.write(f"   📁 Total de archivos: {total_processed}")
        self.stdout.write(f"   🆕 Archivos nuevos: {new_files}")
        self.stdout.write(f"   🔄 Archivos actualizados: {updated_files}")
        self.stdout.write(f"   ✅ Sin cambios: {unchanged_files}")

        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS("✅ Sincronización completada")
            )
        else:
            self.stdout.write(
                self.style.WARNING("🔍 Simulación completada (usa sin --dry-run para aplicar cambios)")
            )

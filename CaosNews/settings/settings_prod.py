"""
Configuración para el entorno de PRODUCCIÓN
- DEBUG False (puede ser True para desarrollo local de producción)
- Base de datos SQLite principal
- CSP estricta pero permite APIs externas necesarias
- Email a consola (cambiar en servidor real)
- Logging con archivos
"""

# Importar todas las configuraciones base
from .settings_base import *
import os

# Secret key para producción local (en servidor real usar variable de entorno)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'local-prod-key-change-in-real-server')

# DEBUG False para producción real, True para desarrollo local de producción
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Hosts permitidos - incluir local para testing y producción
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'caosnews.com', 'www.caosnews.com']

# Database para producción
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Media files - directorio principal para producción
MEDIA_ROOT = BASE_DIR / 'media'

# Email configuration - usar console backend para desarrollo local
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging para producción
LOGGING = get_logging_config(
    log_level='INFO',
    log_file=BASE_DIR / 'caosnews.log'
)

"""
Configuración para el entorno de DESARROLLO
- DEBUG habilitado
- Base de datos SQLite separada
- CSP permisiva para desarrollo
- Email a consola
- Logging detallado
"""

# Importar todas las configuraciones base
from .settings_base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-cp!yxye71r9g#18f!o#-nkil@sip_z#924*-gzlt)2959acye%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database para desarrollo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_dev.sqlite3',
    }
}

# Media files - directorio separado para desarrollo
MEDIA_ROOT = BASE_DIR / 'media_dev'

# Para desarrollo: CSP en modo reporte únicamente (no bloquear)
CSP_REPORT_ONLY = True

# Email backend para desarrollo (envía a consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging para desarrollo con más detalle
LOGGING = get_logging_config(
    log_level='DEBUG',
    log_file=BASE_DIR / 'caosnews_dev.log'
)

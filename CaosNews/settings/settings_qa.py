"""
Configuración para el entorno de QA/TESTING
- Testing manual e integración
- Base de datos SQLite separada para QA
- CSP permisiva para testing
- Email a consola para depuración
- APIs externas configurables
- Logging nivel INFO para QA
- Ideal para: pytest con datos reales, testing manual, integración
"""

# Importar todas las configuraciones base
from .settings_base import *

# Secret key para QA
SECRET_KEY = 'qa-secret-key-for-testing-environment'

# DEBUG deshabilitado para QA
DEBUG = True

# Hosts permitidos para QA
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

# Database para QA
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_qa.sqlite3',
    }
}

# Media files - directorio separado para QA
MEDIA_ROOT = BASE_DIR / 'media_qa'

# Para QA: CSP en modo reporte únicamente (no bloquear para testing)
CSP_REPORT_ONLY = True

# Email backend para QA (envía a consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuración específica para pytest
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Comentado temporalmente para probar imágenes de tiempo
# DISABLE_EXTERNAL_APIS = True

# Logging para QA
LOGGING = get_logging_config(
    log_level='INFO',
    log_file=BASE_DIR / 'caosnews_qa.log'
)

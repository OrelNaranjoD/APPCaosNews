"""
Configuración para el entorno de QA (Testing)
Clona la base de datos de producción y agrega usuarios de prueba
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Secret key específica para QA
SECRET_KEY = "django-qa-secret-key-for-testing-purposes-only"

# DEBUG True para QA (facilita debugging de tests)
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "rest_framework",
    "rest_framework.authtoken",
    "csp",
    "CaosNewsApp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "CaosNews.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "CaosNews.wsgi.application"

# Base de datos clonada de producción para QA
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_qa.sqlite3",
    }
}

# Password validation (relajada para QA)
AUTH_PASSWORD_VALIDATORS = []

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Internationalization
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_TZ = True

# Static files para QA
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "CaosNewsApp" / "static",
]

# Media files para QA - Separado de producción por seguridad
# VENTAJAS DE MANTENER SEPARADO:
# - Aislamiento de datos: Los archivos de QA no afectan producción
# - Prevención de errores: Evita borrar archivos de producción accidentalmente
# - Control de versiones: Cada entorno mantiene su propio estado
# - Seguridad: Los datos de prueba no se mezclan con datos reales
# - Limpieza fácil: Se puede limpiar QA sin afectar producción
#
# Para optimizar espacio en disco, usar comandos de gestión:
# - python manage.py sync_media --method hardlink (enlaces duros)
# - python manage.py clean_qa --media (limpiar cuando no se necesite)
MEDIA_URL = "/media_qa/"
MEDIA_ROOT = BASE_DIR / "media_qa"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Usar el modelo de usuario personalizado para mantener consistencia con producción
AUTH_USER_MODEL = "CaosNewsApp.Usuario"

# Django REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# Content Security Policy configurada para QA (permite carga de imágenes externas)
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": [
            "'self'",
            "data:",
            "blob:",
            "https://openweathermap.org"
        ],
        "font-src": ["'self'", "data:"],
        "connect-src": [
            "'self'",
            "https://api.openweathermap.org"
        ],
        "frame-src": ["'self'"],
        "media-src": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
    }
}

# Configuraciones adicionales de CSP para QA
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "blob:",
    "https://openweathermap.org"
)
CSP_FONT_SRC = ("'self'", "data:")
CSP_CONNECT_SRC = (
    "'self'",
    "https://api.openweathermap.org"
)

# Para QA: Deshabilitar CSP completamente (permitir todo)
CSP_REPORT_ONLY = False
CSP_EXCLUDE_URL_PREFIXES = ("/",)

# Email backend para QA (archivos)
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "qa_emails"

# Configuración específica para testing
# Comentado temporalmente para probar API del tiempo real
# TESTING = True

# Logging para QA
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "qa_debug.log",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "CaosNewsApp": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# Configuraciones adicionales para pruebas optimizadas
# ====================================================

# Acelerar las pruebas con hasher más rápido (solo para testing)
# Comentar esta línea si necesitas seguridad real en QA
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Configuración de caché optimizada para pruebas
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "qa-cache",
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
            "CULL_FREQUENCY": 3,
        },
    }
}

# Configuración para deshabilitar APIs externas en QA
# Comentado temporalmente para probar imágenes de tiempo
# DISABLE_EXTERNAL_APIS = True

# Configuración específica para pytest
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Configuración de cookies para QA
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Variables específicas para identificar el entorno QA
QA_ENVIRONMENT = True
TESTING_WITH_REAL_DATA = True

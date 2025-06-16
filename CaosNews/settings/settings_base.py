"""
Configuración BASE para todos los entornos de CaosNews
Contiene todas las configuraciones comunes que comparten todos los entornos.
Los archivos específicos de entorno solo sobrescriben lo necesario.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'rest_framework.authtoken',
    'csp',
    'CaosNewsApp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'CaosNews.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'CaosNewsApp.context_processors.search_query',
            ],
        },
    },
]

WSGI_APPLICATION = 'CaosNews.wsgi.application'

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'CaosNewsApp.validators.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'CaosNewsApp.validators.ComplexPasswordValidator',
    },
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'CaosNewsApp.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'CaosNewsApp.views.custom_exception_handler'
}

# Content Security Policy - Configuración común para todos los entornos
SELF_DIRECTIVE = "'self'"
CSP_DIRECTIVES = {
    'default-src': [SELF_DIRECTIVE],
    'script-src': [SELF_DIRECTIVE, "'unsafe-inline'", "'unsafe-eval'"],
    'style-src': [SELF_DIRECTIVE, "'unsafe-inline'"],
    'img-src': [SELF_DIRECTIVE, "data:", "blob:", "https://openweathermap.org"],
    'font-src': [SELF_DIRECTIVE, "data:"],
    'connect-src': [SELF_DIRECTIVE, "https://api.openweathermap.org"],
    'frame-src': [SELF_DIRECTIVE],
    'media-src': [SELF_DIRECTIVE],
    'object-src': ["'none'"],
    'base-uri': [SELF_DIRECTIVE],
    'form-action': [SELF_DIRECTIVE],
}

CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': CSP_DIRECTIVES
}

# Configuraciones CSP para django-csp
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

# Logging base configuration
def get_logging_config(log_level='INFO', log_file=None):
    """
    Función helper para generar configuración de logging
    Los entornos pueden sobrescribir log_level y log_file según necesiten
    """
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    }

    root_handlers = ['console']

    if log_file:
        handlers['file'] = {
            'class': 'logging.FileHandler',
            'filename': log_file,
            'formatter': 'verbose',
        }
        root_handlers.append('file')

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': handlers,
        'root': {
            'handlers': root_handlers,
            'level': log_level,
        },
        'loggers': {
            'django': {
                'handlers': root_handlers,
                'level': log_level,
                'propagate': False,
            },
            'CaosNewsApp': {
                'handlers': root_handlers,
                'level': log_level,
                'propagate': False,
            },
        },
    }

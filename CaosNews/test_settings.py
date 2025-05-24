"""
Configuración de Django para pruebas
"""
from .settings import *
import tempfile
import os

# Configuración específica para pruebas
DEBUG = False  # Cambiar a False para acelerar

# Base de datos temporal que se elimina automáticamente
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(tempfile.gettempdir(), 'test_caos_news.db'),
        'OPTIONS': {
            'timeout': 20,
        },
        'TEST': {
            'NAME': os.path.join(tempfile.gettempdir(), 'test_caos_news_test.db'),
        }
    }
}

# Acelerar las pruebas con hasher más rápido
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Usar migraciones pero solo las esenciales
# Esto es más rápido que recrear tablas cada vez

# Configuración para pruebas con Selenium
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Configuración de archivos estáticos para pruebas
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Configuración de medios para pruebas
MEDIA_ROOT = BASE_DIR / 'media'

# Logging simplificado para pruebas
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

# Configuración de caché en memoria para pruebas
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Desactivar CSP para pruebas
CSP_DEFAULT_SRC = None

# Configuración para deshabilitar APIs externas en pruebas
DISABLE_EXTERNAL_APIS = True

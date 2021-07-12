"""Base settings file; used by manage.py. All settings can be overridden via
local_settings.py"""
import os

from django.utils.crypto import get_random_string

ALLOWED_HOSTS = [
    value for key, value in os.environ.items()
    if key.startswith('ALLOWED_HOST')
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'regcore',
    'regcore.search',
    'regcore.supplementary_content',
    'django.contrib.postgres',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

STATIC_URL = "/static/"

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_string(50))

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'UNAUTHENTICATED_USER': None,
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'eregs.db'
    }
}

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]
    }
}]

ROOT_URLCONF = 'regcore.urls'

DEBUG = True

# Configurable storage backends, keyed by data_type (e.g. regulations, diffs)
# If a key is not set, defaults to regcore.db.django_models versions
BACKENDS = {}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'ERROR'
        }
    }
}

# Batch size used in `bulk_create`; defaults to a conservative value to avoid
# hitting SQLite limits
BATCH_SIZE = 50

# Lower bound for search results to appear when using pgsql search
PG_SEARCH_RANK_CUTOFF = 0.15

_envvars = ('HTTP_AUTH_USER', 'HTTP_AUTH_PASSWORD')
for var in _envvars:
    globals()[var] = os.environ.get(var)

try:
    from local_settings import *
except ImportError:
    pass

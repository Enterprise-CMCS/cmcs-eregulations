"""
Django settings for cmcs_regulations project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", 'django-insecure-u!&%t$qxa23zn1f*-+4pngd(p=nl_m3()+v839+fa=06y9(*)n')


ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST'), 'localhost', '.cms.gov']

# Application definition

INSTALLED_APPS = [
    "debug_toolbar",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'rest_framework',
    'regulations',
    'regcore',
    'regcore.search',
    'resources',
    'solo',
    'django_opensearch_dsl',
    'corsheaders',
    'drf_spectacular',
    'django.contrib.sitemaps',
    'django_jsonform',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'regulations.middleware.JsonErrors',
    'regulations.middleware.NoIndex',
    'regcore.middleware.HtmlApi',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

TEMPLATE_CONTEXT_PROCESSORS = (

    # Put your context processors here

    'django.core.context_processors.request',
    'regulations.context_processors.site_config',
    'regcore.context_processors.regcore_config',
)

ROOT_URLCONF = 'cmcs_regulations.urls'

STATIC_URL = os.environ.get("STATIC_URL", None)
STATIC_ROOT = os.environ.get("STATIC_ROOT", None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", False)

WORKING_DIR = os.environ.get("WORKING_DIR", "/var/lib/eregs")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "context_processors": (
                # "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                'django.contrib.auth.context_processors.auth',
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "cmcs_regulations.context_processors.google_analytics",
                "cmcs_regulations.context_processors.base_url",
                "cmcs_regulations.context_processors.automated_testing",
                'regulations.context_processors.site_config',
                'regcore.context_processors.regcore_config',
            ),
        },
        "DIRS": [
            BASE_DIR / 'templates',
        ],
        "APP_DIRS": True,
    },
]

WSGI_APPLICATION = 'cmcs_regulations.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.environ.get('DB_USER', 'eregs'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sgere'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'NAME': os.environ.get('DB_NAME', 'eregs'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_L10N = False

USE_TZ = False

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

API_BASE = os.environ.get('EREGS_API_BASE', '')

GUIDANCE_DIR = os.environ.get("SIDEBAR_CONTENT_DIR")

HTTP_AUTH_USER = os.environ.get("HTTP_AUTH_USER")
HTTP_AUTH_PASSWORD = os.environ.get("HTTP_AUTH_PASSWORD")

GA_ID = os.environ.get("GA_ID")

BASE_URL = os.environ.get("BASE_URL")


OPENSEARCH_DSL = {
    'default': {
        'hosts': 'opensearch-node1'
    },
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "http://0.0.0.0:8081",
    # Storybook
    "http://localhost:6006"
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"https://\w+\.execute-api.us-east-1\.amazonaws\.com$",
    r"https://\w+\.cloudfront\.net"
]

SPECTACULAR_SETTINGS = {
    'TITLE': 'CMCS eRegulations API',
    'DESCRIPTION': 'Medicaid and CHIP regulation content and associated supplemental content (such as subregulatory guidance)'
}

LOGIN_URL = "/admin"

if DEBUG:
    import os  # only if you haven't already imported this
    import socket  # only if you haven't already imported this
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']

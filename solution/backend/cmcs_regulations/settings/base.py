"""
Django settings for cmcs_regulations project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from datetime import datetime
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", 'django-insecure-u!&%t$qxa23zn1f*-+4pngd(p=nl_m3()+v839+fa=06y9(*)n')


ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST'),
                 'localhost',
                 'regulations-pilot.cms.gov',
                 'eregulations.cms.gov',
                 'host.docker.internal']

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
    'rest_framework_simplejwt',
    'regulations',
    'regcore',
    'regcore.search',
    'resources',
    'solo',
    'corsheaders',
    'drf_spectacular',
    'django.contrib.sitemaps',
    'django.contrib.syndication.views',
    'django_jsonform',
    'file_manager',
    'content_search',
    'mozilla_django_oidc',
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
    'csp.middleware.CSPMiddleware',
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
    'regulations.context_processors.eua_config',
    'cmcs_regulations.context_processors.api_base',
    'regcore.context_processors.regcore_config',
)

ROOT_URLCONF = 'cmcs_regulations.urls'

STATIC_URL = os.environ.get("STATIC_URL", None)
STATIC_ROOT = os.environ.get("STATIC_ROOT", None)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
    "formatters": {
        "simple": {
            "format": "%(levelname)s %(message)s",
        },
    },
}

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
                "cmcs_regulations.context_processors.custom_url",
                "cmcs_regulations.context_processors.survey_url",
                "cmcs_regulations.context_processors.signup_url",
                "cmcs_regulations.context_processors.deploy_number",
                "cmcs_regulations.context_processors.automated_testing",
                'cmcs_regulations.context_processors.api_base',
                'regulations.context_processors.site_config',
                'regulations.context_processors.eua_config',
                'regcore.context_processors.regcore_config',
            ),
        },
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
    },
]

WSGI_APPLICATION = 'cmcs_regulations.wsgi.application'

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

API_BASE = "v3/"  # Note: never include leading forward-slash

GUIDANCE_DIR = os.environ.get("SIDEBAR_CONTENT_DIR")

HTTP_AUTH_USER = os.environ.get("HTTP_AUTH_USER")
HTTP_AUTH_PASSWORD = os.environ.get("HTTP_AUTH_PASSWORD")

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_COLLAPSED': True
}

GA_ID = os.environ.get("GA_ID")

CUSTOM_URL = os.environ.get("CUSTOM_URL")
SURVEY_URL = os.environ.get(
    "SURVEY_URL",
    "https://docs.google.com/forms/d/e/1FAIpQLSdcG9mfTz6Kebdni8YSacl27rIwpGy2a7GsMGO0kb_T7FSNxg/viewform?embedded=true"
)
SIGNUP_URL = os.environ.get(
    "SIGNUP_URL",
    "https://docs.google.com/forms/d/e/1FAIpQLSdcG9mfTz6Kebdni8YSacl27rIwpGy2a7GsMGO0kb_T7FSNxg/viewform?embedded=true"
)

DEPLOY_NUMBER = os.environ.get("DEPLOY_NUMBER", datetime.now())

USE_LOCAL_TEXTRACT = False
# The first text extractor is if it was created by serverless.  If it wasnt then it will use the
# text extractor who's arn you provide in the docker file.

TEXT_EXTRACTOR_ARN = os.environ.get("TEXT_EXTRACTOR_ARN", '')
TEXTRACT_ARN = os.environ.get('TEXTRACT_ARN', '')

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

LOGIN_URL = "/login/"

# Settings for CSP headers
CSP_IMG_SRC = [
    "'self'",
    STATIC_URL,
    "https://*.googletagmanager.com",
    "https://*.google-analytics.com",
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/favicon-32x32.png",
    'data:',
    "https://images.federalregister.gov/",
]
CSP_FRAME_SRC = [
    "'self'",
    STATIC_URL,
    "https://docs.google.com",
    "https://forms.gle"
]

CSP_STYLE_SRC = [
    "'self'",
    "'unsafe-inline'",
    STATIC_URL,
    "https://cdn.jsdelivr.net/npm/@mdi/font@4.x/",
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui.css"
]
CSP_FONT_SRC = [
    "'self'",
    STATIC_URL,
    "https://cdn.jsdelivr.net/npm/@mdi/font@4.x/",
]
CSP_MANIFEST_SRC = [
    "'self'",
    STATIC_URL,
]
CSP_SCRIPT_SRC = [
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    STATIC_URL,
    "https://*.googletagmanager.com",
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js",
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-standalone-preset.js",
]
CSP_SCRIPT_SRC_ELEM = [
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    STATIC_URL,
    "https://*.googletagmanager.com",
    "https://cdn.jsdelivr.net/npm/vue@2.7.15",
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js",
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-standalone-preset.js",
]
CSP_CONNECT_SRC = [
    "'self'",
    STATIC_URL,
    "https://*.googletagmanager.com",
    "https://*.google-analytics.com",
    "http://*.analytics.google.com",
]
CSP_INCLUDE_NONCE_IN = ["script-src"]

BASIC_SEARCH_FILTER = os.environ.get("BASIC_SEARCH_FILTER", .1)
QUOTED_SEARCH_FILTER = os.environ.get("QUOTED_SEARCH_FILTER", .01)

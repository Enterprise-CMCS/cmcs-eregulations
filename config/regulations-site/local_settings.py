import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'regulations.apps.RegulationsConfig',
)

ROOT_URLCONF = 'regulations.urls'

DATABASES = {}

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

SIDEBARS = (
    'cmcs.regulations.sidebar.guidance.Guidance',
    'regulations.generator.sidebar.print_part.PrintPart',
)

STATIC_URL = os.environ.get("STATIC_URL", None)
STATIC_ROOT = os.environ.get("STATIC_ROOT", None)

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
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "regulations.context.eregs_globals",
            ),
            # List of callables that know how to import templates from various
            # sources.
            "loaders": [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
        "DIRS": [
            "%s/templates" % BASE_DIR,
            os.environ.get("SIDEBAR_CONTENT_DIR"),
        ],
    },
]

GUIDANCE_DIR = os.environ.get("SIDEBAR_CONTENT_DIR")

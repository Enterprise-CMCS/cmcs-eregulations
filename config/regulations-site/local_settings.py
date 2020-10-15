import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'regulations.apps.RegulationsConfig',
    'notice_comment',
    # TODO: can django be convinced it can live without the following?
    'django.contrib.contenttypes',
    'django.contrib.auth',
)

SIDEBARS = (
    'regulations.generator.sidebar.analyses.Analyses',
    'regulations.generator.sidebar.help.Help',
    'regulations.generator.sidebar.print_part.PrintPart',
    'guidance.guidance.Guidance',
)

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
                ('django.template.loaders.cached.Loader', (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader'))
            ],
        },
        "DIRS": [
            "%s/templates" % BASE_DIR,
            "/var/lib/eregs/guidance/content",
        ],
    },
]

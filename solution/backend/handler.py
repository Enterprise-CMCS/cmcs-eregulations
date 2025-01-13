"""
WSGI config for serverless_django project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from mangum import Mangum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")

application = get_wsgi_application()

# Mangum wraps a WSGI/ASGI callable so AWS Lambda can handle requests.
lambda_handler = Mangum(application)


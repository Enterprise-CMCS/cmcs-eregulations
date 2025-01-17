"""
WSGI config for cmcs_regulations project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from mangum import Mangum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmcs_regulations.settings')

application = get_wsgi_application()
lambda_handler = Mangum(application, lifespan="off")

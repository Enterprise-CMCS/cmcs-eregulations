import os

from django.core.asgi import get_asgi_application
from mangum import Mangum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")

# Initialize Django
django_asgi_app = get_asgi_application()
handler = Mangum(django_asgi_app, lifespan="off")


def lambda_handler(event, context):
    return handler(event, context)

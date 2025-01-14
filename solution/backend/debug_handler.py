# debug_handler.py
import sys
import os
import traceback
import logging
import mangum
from django.core.wsgi import get_wsgi_application
from django.core.asgi import get_asgi_application

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

def lambda_handler(event, context):
    try:
        logger.debug("Event received: %s", event)
        logger.debug("Context received: %s", vars(context))
        logger.debug("Environment variables: %s", dict(os.environ))
        logger.debug("Current directory: %s", os.getcwd())
        logger.debug("Directory contents: %s", os.listdir())
        logger.debug("Python path: %s", sys.path)
        
        # Initialize Django ASGI application
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
        application = get_asgi_application()
        
        # Create Mangum handler
        handler = mangum.Mangum(application, lifespan="off")
        
        # Handle the request
        return handler(event, context)
    except Exception as e:
        logger.error("Exception occurred")
        logger.error(e)
        logger.error(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": str(e),
            "headers": {"content-type": "text/plain; charset=utf-8"},
            "multiValueHeaders": {},
            "isBase64Encoded": False
        }
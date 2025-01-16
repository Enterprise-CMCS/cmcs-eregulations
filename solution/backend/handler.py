# import os
# import sys
# import logging
# import traceback
# from cmcs_regulations.wsgi import lambda_handler as wsgi_handler

# # Configure logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[logging.StreamHandler(sys.stdout)]
# )
# logger = logging.getLogger()

# def lambda_handler(event, context):
#     try:
#         logger.debug(f"Lambda event: {event}")
#         logger.debug(f"Lambda context: {vars(context)}")
#         logger.debug(f"Environment: {dict(os.environ)}")
        
#         # Call the wsgi handler from cmcs_regulations.wsgi
#         response = wsgi_handler(event, context)
#         logger.debug(f"Lambda response: {response}")
#         return response
#     except Exception as e:
#         logger.error(f"Error processing request: {str(e)}")
#         logger.error(f"Stack trace: {traceback.format_exc()}")
#         return {
#             "statusCode": 500,
#             "body": str(e),
#             "headers": {
#                 "Content-Type": "text/plain",
#             },
#             "isBase64Encoded": False
#         }
import os
import sys
import logging
import traceback
from django.core.wsgi import get_wsgi_application
from a2wsgi import ASGIMiddleware
from mangum import Mangum

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('lambda_debug')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmcs_regulations.settings')

# Create and wrap the application
try:
    logger.debug("Initializing Django WSGI application...")
    wsgi_app = get_wsgi_application()
    logger.debug("WSGI application initialized successfully")

    logger.debug("Wrapping WSGI app with ASGIMiddleware...")
    asgi_app = ASGIMiddleware(wsgi_app)
    logger.debug("ASGI middleware wrapped successfully")

    logger.debug("Creating Mangum handler...")
    # Configure Mangum with additional options
    handler = Mangum(
        asgi_app,
        api_gateway_base_path=os.environ.get('API_GATEWAY_BASE_PATH', '/'),
        lifespan="off",  # Disable lifespan for WSGI compatibility
        logger=logger
    )
    logger.debug("Mangum handler created successfully")

except Exception as e:
    logger.error(f"Error during application initialization: {str(e)}")
    logger.error(traceback.format_exc())
    raise

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    try:
        logger.debug("=== Lambda Event Details ===")
        logger.debug(f"Event: {event}")
        logger.debug(f"Context: {vars(context)}")

        # Log relevant request details
        if 'httpMethod' in event:
            logger.debug(f"HTTP Method: {event['httpMethod']}")
        if 'path' in event:
            logger.debug(f"Path: {event['path']}")
        if 'headers' in event:
            logger.debug(f"Headers: {event['headers']}")

        # Handle the request
        logger.debug("Calling Mangum handler...")
        response = handler(event, context)
        logger.debug(f"Response: {response}")

        return response

    except Exception as e:
        logger.error("=== Lambda Handler Error ===")
        logger.error(f"Error Type: {type(e)}")
        logger.error(f"Error Message: {str(e)}")
        logger.error(f"Stack Trace:\n{traceback.format_exc()}")

        return {
            "statusCode": 500,
            "body": str(e),
            "headers": {
                "Content-Type": "text/plain",
                "X-Error-Type": str(type(e).__name__)
            },
            "isBase64Encoded": False
        }
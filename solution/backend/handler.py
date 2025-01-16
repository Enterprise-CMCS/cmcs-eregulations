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

# Initialize applications with detailed error handling
try:
    logger.debug("=== Initializing Applications ===")
    
    logger.debug("Getting WSGI application...")
    wsgi_app = get_wsgi_application()
    logger.debug("WSGI application initialized successfully")
    
    logger.debug("Wrapping with ASGIMiddleware...")
    asgi_app = ASGIMiddleware(wsgi_app)
    logger.debug("ASGI middleware wrapped successfully")
    
    logger.debug("Creating Mangum handler...")
    # Initialize Mangum without the logger parameter
    handler = Mangum(
        asgi_app,
        api_gateway_base_path=os.environ.get('API_GATEWAY_BASE_PATH', '/'),
        lifespan="off"
    )
    logger.debug("Mangum handler created successfully")

except Exception as e:
    logger.error("=== Application Initialization Error ===")
    logger.error(f"Error Type: {type(e).__name__}")
    logger.error(f"Error Message: {str(e)}")
    logger.error(f"Stack Trace:\n{traceback.format_exc()}")
    raise

def lambda_handler(event, context):
    """
    AWS Lambda handler function with enhanced error logging
    """
    try:
        logger.debug("=== New Lambda Invocation ===")
        
        # Log the full event and context
        logger.debug("--- Event Details ---")
        logger.debug(f"Event: {event}")
        logger.debug("--- Context Details ---")
        logger.debug(f"Context: {vars(context)}")
        
        # Log specific request details
        logger.debug("--- Request Details ---")
        http_method = event.get('requestContext', {}).get('http', {}).get('method')
        path = event.get('requestContext', {}).get('http', {}).get('path')
        source_ip = event.get('requestContext', {}).get('http', {}).get('sourceIp')
        headers = event.get('headers', {})
        query_params = event.get('queryStringParameters')
        
        logger.debug(f"HTTP Method: {http_method}")
        logger.debug(f"Path: {path}")
        logger.debug(f"Source IP: {source_ip}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Query Parameters: {query_params}")

        # Handle the request
        logger.debug("Calling Mangum handler...")
        response = handler(event, context)
        
        # Log the response
        logger.debug("--- Response Details ---")
        logger.debug(f"Response: {response}")
        
        return response

    except Exception as e:
        logger.error("=== Lambda Handler Error ===")
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error(f"Error Message: {str(e)}")
        logger.error(f"Stack Trace:\n{traceback.format_exc()}")
        
        # Return error response
        return {
            "statusCode": 500,
            "body": f"Internal Server Error: {type(e).__name__} - {str(e)}",
            "headers": {
                "Content-Type": "text/plain",
                "X-Error-Type": type(e).__name__
            },
            "isBase64Encoded": False
        }
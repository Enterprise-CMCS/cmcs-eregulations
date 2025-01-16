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
import inspect
from cmcs_regulations.wsgi import lambda_handler as wsgi_lambda_handler, application

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('lambda_debug')

def lambda_handler(event, context):
    try:
        # Debug environment
        logger.debug("=== Environment Variables ===")
        logger.debug(dict(os.environ))

        # Debug Django application
        logger.debug("=== Django Application Info ===")
        logger.debug(f"Application type: {type(application)}")
        logger.debug(f"Application callable: {inspect.isfunction(application)}")
        logger.debug(f"Application attributes: {dir(application)}")

        # Debug Mangum handler
        logger.debug("=== Mangum Handler Info ===")
        logger.debug(f"WSGI Lambda handler type: {type(wsgi_lambda_handler)}")
        logger.debug(f"WSGI Lambda handler attributes: {dir(wsgi_lambda_handler)}")
        
        # Debug event and context
        logger.debug("=== Lambda Event ===")
        logger.debug(f"Event type: {type(event)}")
        logger.debug(f"Event content: {event}")
        logger.debug("=== Lambda Context ===")
        logger.debug(f"Context type: {type(context)}")
        logger.debug(f"Context dir: {dir(context)}")
        
        # Debug request path and method
        if 'path' in event:
            logger.debug(f"Request path: {event.get('path')}")
        if 'httpMethod' in event:
            logger.debug(f"HTTP method: {event.get('httpMethod')}")
        if 'headers' in event:
            logger.debug(f"Request headers: {event.get('headers')}")

        # Track handler execution
        logger.debug("=== Execution Flow ===")
        logger.debug("Before calling wsgi_lambda_handler")
        response = wsgi_lambda_handler(event, context)
        logger.debug("After calling wsgi_lambda_handler")
        logger.debug(f"Response: {response}")

        return response

    except TypeError as e:
        logger.error("=== TypeError Exception ===")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        # Get the function signature that caused the error
        tb = traceback.extract_tb(sys.exc_info()[2])
        for filename, line, func, text in tb:
            logger.error(f"File: {filename}, Line: {line}, Function: {func}, Text: {text}")
        
        return {
            "statusCode": 500,
            "body": f"TypeError: {str(e)}\nStack trace: {traceback.format_exc()}",
            "headers": {"Content-Type": "text/plain"},
            "isBase64Encoded": False
        }
    except Exception as e:
        logger.error("=== General Exception ===")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        
        return {
            "statusCode": 500,
            "body": str(e),
            "headers": {"Content-Type": "text/plain"},
            "isBase64Encoded": False
        }
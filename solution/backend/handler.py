import os
import sys
import logging
import traceback
from cmcs_regulations.wsgi import lambda_handler as wsgi_handler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger()

def lambda_handler(event, context):
    try:
        logger.debug(f"Lambda event: {event}")
        logger.debug(f"Lambda context: {vars(context)}")
        logger.debug(f"Environment: {dict(os.environ)}")
        
        # Call the wsgi handler from cmcs_regulations.wsgi
        response = wsgi_handler(event, context)
        logger.debug(f"Lambda response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return {
            "statusCode": 500,
            "body": str(e),
            "headers": {
                "Content-Type": "text/plain",
            },
            "isBase64Encoded": False
        }
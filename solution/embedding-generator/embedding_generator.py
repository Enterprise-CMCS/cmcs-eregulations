import logging
import os
from typing import Any

from .utils import lambda_response

# Initialize the root logger. All other loggers will automatically inherit from this one.
root_logger = logging.getLogger()
if root_logger.handlers:
    root_logger.removeHandler(root_logger.handlers[0])  # Remove the default handler to avoid duplicate logs
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s')
ch.setFormatter(formatter)
root_logger.addHandler(ch)
root_logger.setLevel(logging.INFO)

# Initialize the logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def handler(event: dict, context: Any) -> dict:
    """
    AWS Lambda handler function to process embedding generation requests.
    This function initializes logging, retrieves configuration, and performs embedding generation.
    It handles both synchronous and asynchronous requests, and sends results to eRegs if applicable.
    Args:
        event (dict): The event data passed to the Lambda function, expected to contain configuration parameters.
        context (Any): The context object provided by AWS Lambda, used for managing execution time.
    Returns:
        dict: A response dictionary containing the status code and success or failure message.
    Raises:
        Exception: If an error occurs during processing and the Lambda is invoked by SQS.
    """

    logger.info("Log level is set to %s.", logging.getLevelName(logger.getEffectiveLevel()))
    return lambda_response(200, "Embedding generation handler is not yet implemented.")

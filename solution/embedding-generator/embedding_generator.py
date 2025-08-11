import json
import logging
import os
from typing import Any

from lambda_common.utils import (
    get_boto3_client,
    get_config,
    lambda_response,
    configure_authorization,
    send_results,
)

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

    # Get config
    config = get_config(event)

    # Check for required parameters in the event
    logger.info("Retrieving required parameters from event.")
    try:
        chunk_id = config["id"]
        upload_url = config["upload_url"]
        text = config["text"]
    except KeyError:
        return lambda_response(400, "You must include 'id', 'upload_url', and 'text' in the request body.")

    # Get optional parameters
    model_id = config.get("model_id", "amazon.titan-embed-text-v2:0")
    dimensions = config.get("dimensions", 512)
    normalize = config.get("normalize", True)
    max_text_length = config.get("max_text_length", 20000)  # Default to 20,000 characters to avoid the model's token limit
    max_text_length += 2000  # Add room for the chunk overlap; 1,000 characters on each side

    # Validate the text input
    text = " ".join(text.split())  # Normalize whitespace
    if not text or len(text) > max_text_length:
        return lambda_response(400, f"Text must be a non-empty string and less than {max_text_length} characters long.")

    # Configure authorization
    authorization = None
    if config.get("auth"):
        try:
            authorization = configure_authorization(config["auth"])
        except Exception as e:
            return lambda_response(400, f"Failed to configure authorization: {str(e)}")

    # Initialize the Bedrock client
    try:
        bedrock_client = get_boto3_client("bedrock-runtime", config)
    except Exception as e:
        return lambda_response(500, f"Failed to initialize Bedrock client: {str(e)}")

    # Create payload
    payload = {
        "inputText": text,
        "dimensions": dimensions,
        "normalize": normalize,
    }

    # Perform embedding generation and send results
    try:
        logger.info("Generating embeddings for chunk ID %s.", chunk_id)
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(payload),
            contentType='application/json',
            accept='application/json',
        )
        embeddings = json.loads(response.get("body").read())["embedding"]

        logger.info("Embeddings generated successfully for chunk ID %s. Sending results.", chunk_id)
        send_results(
            chunk_id,
            upload_url,
            authorization,
            id=chunk_id,
            embeddings=embeddings,
        )
    except Exception as e:
        if "sqs_group" in config:
            logger.error("An error occurred: %s", str(e))
            raise e
        return lambda_response(500, f"An error occurred: {str(e)}")

    return lambda_response(200, "Embedding generation completed successfully.")

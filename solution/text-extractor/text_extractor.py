import json
import logging
import os
import re

import requests

from .backends import (
    BackendException,
    BackendInitException,
    FileBackend,
)
from .extractors import (
    Extractor,
    ExtractorException,
    ExtractorInitException,
)

# Initialize the root logger. All other loggers will automatically inherit from this one.
logger = logging.getLogger()
logger.removeHandler(logger.handlers[0])  # Remove the default handler to avoid duplicate logs
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def lambda_response(status_code: int, loglevel: int, message: str) -> dict:
    logging.log(loglevel, message)
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": message}),
    }


def lambda_success(message: str) -> dict:
    return lambda_response(200, logging.INFO, message)


def lambda_failure(status_code: int, message: str) -> dict:
    return lambda_response(status_code, logging.ERROR, message)


def handler(event: dict, context: dict) -> dict:
    logger.info("Log level is set to %s.", logging.getLevelName(logger.getEffectiveLevel()))

    # Retrieve configuration from event dict
    logger.info("Retrieving Lambda event dictionary.")
    if "body" not in event:
        # Assume we are invoked directly
        config = event
        logger.debug("No 'body' key present in event, assuming direct invocation.")
    else:
        try:
            config = json.loads(event["body"])
        except Exception:
            return lambda_failure(400, "Unable to parse body as JSON.")

    # Retrieve required arguments
    logger.info("Retrieving required parameters from event.")
    try:
        resource_id = config["id"]
        uri = config["uri"]
        post_url = config["post_url"]
        token = config["token"]
    except KeyError:
        return lambda_failure(400, "You must include 'id', 'uri', 'token', and 'post_url' in the request body.")

    # Retrieve the file
    logger.info("Starting file retrieval.")
    try:
        backend_type = config.get("backend", "web").lower()
        backend = FileBackend.get_backend(backend_type, config)
        file = backend.get_file(uri)
    except BackendInitException as e:
        return lambda_failure(500, f"Failed to initialize backend: {str(e)}")
    except BackendException as e:
        return lambda_failure(500, f"Failed to retrieve file: {str(e)}")
    except Exception as e:
        return lambda_failure(500, f"Backend unexpectedly failed: {str(e)}")

    try:
        file_type = uri.lower().split('.')[-1]
    except Exception as e:
        return lambda_failure(500, f"Failed to determine file type: {str(e)}")

    # Run extractor
    logger.info("Starting text extraction.")
    try:
        extractor = Extractor.get_extractor(file_type, config)
        text = extractor.extract(file)
    except ExtractorInitException as e:
        return lambda_failure(500, f"Failed to initialize text extractor: {str(e)}")
    except ExtractorException as e:
        return lambda_failure(500, f"Failed to extract text: {str(e)}")
    except Exception as e:
        return lambda_failure(500, f"Extractor unexpectedly failed: {str(e)}")

    # Strip unneeded data out of the extracted text
    text = re.sub(r'[\n\s]+', ' ', text).strip()

    # Send result to eRegs
    logger.info("Sending extracted text to POST URL.")
    resp = ''
    header = {'Authorization': f'Bearer {token}'}
    try:
        resp = requests.post(
            post_url,
            headers=header,
            json={
                "id": resource_id,
                "text": text,
            },
            timeout=60,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return lambda_failure(500, f"Failed to POST results: {str(e)}")
    except Exception as e:
        return lambda_failure(500, f"POST unexpectedly failed: {str(e)}")

    # Return success code
    return lambda_success(f"Function exited normally. {resp.content}")

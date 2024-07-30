import logging
import os

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
from .utils import (
    clean_output,
    get_config,
    lambda_failure,
    lambda_success,
    configure_authorization,
)

# Initialize the root logger. All other loggers will automatically inherit from this one.
logger = logging.getLogger()
if logger.handlers:
    logger.removeHandler(logger.handlers[0])  # Remove the default handler to avoid duplicate logs
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def handler(event: dict, context: dict) -> dict:
    logger.info("Log level is set to %s.", logging.getLevelName(logger.getEffectiveLevel()))

    # Retrieve configuration from event dict
    try:
        config = get_config(event)
    except Exception as e:
        return lambda_failure(400, f"Failed to get Lambda configuration: {str(e)}")

    # Retrieve required arguments
    logger.info("Retrieving required parameters from event.")
    try:
        uri = config["uri"]
        post_url = config["post_url"]
    except KeyError:
        return lambda_failure(400, "You must include 'uri', 'token', and 'post_url' in the request body.")

    # Configure authorization, if desired
    authorization = None
    if "auth" in config:
        try:
            authorization = configure_authorization(config["auth"])
        except Exception as e:
            return lambda_failure(400, f"Failed to configure authorization: {str(e)}")

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

    # Determine the file's content type
    try:
        file_type = Extractor.get_file_type(file)
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

    # Strip control characters and unneeded data out of the extracted text
    text = clean_output(text)

    # Send result to eRegs
    logger.info("Sending extracted text to POST URL.")
    headers = {'Authorization': authorization} if authorization else {}
    try:
        resp = requests.patch(
            post_url,
            headers=headers,
            json={
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
    return lambda_success("Function exited normally.")

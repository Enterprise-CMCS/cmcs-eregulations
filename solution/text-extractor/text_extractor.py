import logging
import os

import requests
import magic
import filetype

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

    # Determine the file's MIME type.
    # Uses a 2-stage approach: filetype first, then magic if filetype fails.
    # Filetype is more accurate in general, but magic supports more files types.
    # Magic docs recommend using the first 2048 bytes of the file, but this isn't always accurate.
    try:
        file_type = filetype.guess_mime(file)
        if not file_type or file_type == "application/octet-stream":
            raise Exception
    except Exception:
        try:
            file_type = magic.from_buffer(file, mime=True)
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

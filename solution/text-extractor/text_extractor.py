import logging
import os
import time
from typing import Any

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
    lambda_response,
    configure_authorization,
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

# Global variable representing the time that the file was retrieved
# If None, it means the file has not been retrieved yet
retrieval_finished_time = None


class TextExtractorException(Exception):
    pass


def start_text_extractor(config: dict, context: Any) -> None:
    global retrieval_finished_time

    # Retrieve required arguments
    logger.info("Retrieving required parameters from event.")
    try:
        resource_id = config["id"]
        uri = config["uri"]
        upload_url = config["upload_url"]
    except KeyError:
        raise TextExtractorException("You must include 'id', 'uri', 'token', and 'upload_url' in the request body.")

    # Configure authorization, if desired
    authorization = None
    if config.get("auth"):
        try:
            authorization = configure_authorization(config["auth"])
        except Exception as e:
            raise TextExtractorException(f"Failed to configure authorization: {str(e)}")

    if config.get("job_id"):
        # If a job ID is provided, we assume this invocation is a continuation of a previous job being processed
        # by an external service, and so we skip the file retrieval step.
        logger.info("Job ID found in config: %s, skipping file retrieval.", config["job_id"])
        file = None
    else:
        # Retrieve the file
        logger.info("Starting file retrieval from URI: %s", uri)
        try:
            backend_type = config.get("backend", "web").lower()
            backend = FileBackend.get_backend(backend_type, config)
            file = backend.get_file(uri)
            # Set the retrieval finished time
            retrieval_finished_time = time.time()
            logger.info("File retrieved successfully. Size: %d bytes", len(file))
        except BackendInitException as e:
            raise TextExtractorException(f"Failed to initialize backend: {str(e)}")
        except BackendException as e:
            # If retrieval fails, we should still delay if configured to do so
            retrieval_finished_time = time.time()
            raise TextExtractorException(f"Failed to retrieve file: {str(e)}")
        except Exception as e:
            # If retrieval fails for an unexpected reason, we should still delay if configured to do so
            retrieval_finished_time = time.time()
            raise TextExtractorException(f"Backend unexpectedly failed: {str(e)}")

    if config.get("file_type"):
        # If a file type is provided, we use it directly instead of determining it from the file
        file_type = config["file_type"]
        logger.info("Attempting to use the provided file type: %s", file_type)
    else:
        # Determine the file's content type
        try:
            file_type = Extractor.get_file_type(file)
        except Exception as e:
            raise TextExtractorException(f"Failed to determine file type: {str(e)}")

    # Run extractor
    logger.info("Starting text extraction.")
    try:
        extractor = Extractor.get_extractor(file_type, config)
        text = extractor.extract(file)
    except ExtractorInitException as e:
        raise TextExtractorException(f"Failed to initialize text extractor: {str(e)}")
    except ExtractorException as e:
        raise TextExtractorException(f"Failed to extract text: {str(e)}")
    except Exception as e:
        raise TextExtractorException(f"Extractor unexpectedly failed: {str(e)}")

    # If no text was extracted, we will skip sending results to eRegs, but still return a successful response
    if not text:
        logger.info(
            "No text was extracted from the file, but no errors occurred. "
            "This may be expected for certain file types, empty files, or files that will be processed by an external service."
        )
        if context.get_remaining_time_in_millis() > 60 * 1000:
            # If we have more than 60 seconds left, we will sleep for a minute to allow for any asynchronous processing to occur
            # This is useful if the file is being processed by an external service that may take some time to complete
            logger.info("Sleeping for 1 minute before finishing to allow for any potential asynchronous processing to occur.")
            time.sleep(60)
        return

    # Strip control characters and unneeded data out of the extracted text
    text = clean_output(text)

    # Send result to eRegs
    logger.info("Sending extracted text to PATCH URL.")
    headers = {'Authorization': authorization} if authorization else {}
    try:
        resp = requests.patch(
            upload_url,
            headers=headers,
            json={
                "id": resource_id,
                "text": text,
            },
            timeout=60,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        if hasattr(e, "response") and hasattr(e.response, "text") and e.response.text:
            raise TextExtractorException(f"Failed to PATCH results with status code {e.response.status_code}: {e.response.text}")
        raise TextExtractorException(f"Failed to PATCH results: {str(e)}")
    except Exception as e:
        raise TextExtractorException(f"PATCH unexpectedly failed: {str(e)}")


def handler(event: dict, context: Any) -> dict:
    logger.info("Log level is set to %s.", logging.getLevelName(logger.getEffectiveLevel()))

    global retrieval_finished_time
    sqs_group = None
    retrieval_delay = 0

    try:
        config = get_config(event)
        sqs_group = config.get("sqs_group")
        retrieval_delay = config.get("retrieval_delay", 0)
        start_text_extractor(config, context)
        return lambda_response(200, "Text extraction completed successfully.")
    except Exception as e:
        if sqs_group:
            logger.error("An error occurred: %s", str(e))
            raise e
        return lambda_response(500, f"An error occurred: {str(e)}")
    finally:
        time_since_retrieval = time.time() - (retrieval_finished_time or 0)
        delay_time = retrieval_delay - time_since_retrieval
        remaining_time = context.get_remaining_time_in_millis() / 1000  # Convert to seconds
        delay_time = delay_time if remaining_time > delay_time else remaining_time - 1  # Don't delay more than the time left
        if retrieval_finished_time and time_since_retrieval < retrieval_delay:
            logger.info(
                "%sWaiting for %d seconds before finishing.",
                f"[Group: {sqs_group}] " if sqs_group else "",
                delay_time,
            )
            time.sleep(delay_time)

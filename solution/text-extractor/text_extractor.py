import base64
import logging
import os
import time
from typing import Any

import boto3

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
    send_results,
    chunk_text,
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


def extract_text(config: dict, context: Any) -> tuple[str, str, float, str]:
    """
    Extracts text from a file specified in the configuration, handling file retrieval, type detection, and extraction.
    This function supports both direct file retrieval and continuation of asynchronous jobs (via job_id).
    It determines the file type (if not provided), initializes the appropriate extractor, and processes the file to extract text.
    Handles various error conditions and logs progress throughout the process.
    Args:
        config (dict): Configuration dictionary containing parameters such as 'uri', 'backend', 'file_type', and optionally 'job_id'.
        context (Any): Context object, expected to provide a method `get_remaining_time_in_millis()` for time management.
    Returns:
        tuple[str, str, float, str]:
            - Extracted text as a string (or None if extraction failed or no text found).
            - File type as a string (or None if undetermined).
            - Retrieval finished time as a float timestamp (or None if not applicable).
            - Error message as a string (or None if successful).
    """

    retrieval_finished_time = None

    if config.get("job_id"):
        # If a job ID is provided, we assume this invocation is a continuation of a previous job being processed
        # by an external service, and so we skip the file retrieval step.
        logger.info("Job ID found in config: %s, skipping file retrieval.", config["job_id"])
        file = None
    elif config.get("content"):
        # If content is provided directly, we decode it from base64
        logger.info("Decoding file content from base64.")
        try:
            file = base64.b64decode(config["content"].encode("utf-8"))
            retrieval_finished_time = time.time()
            logger.info("File content decoded successfully. Size: %d bytes", len(file))
        except Exception as e:
            return None, None, None, f"Failed to decode file content: {str(e)}"
    elif config.get("uri"):
        # Retrieve the file
        logger.info("Starting file retrieval from URI: %s", config["uri"])
        try:
            backend_type = config.get("backend", "web").lower()
            backend = FileBackend.get_backend(backend_type, config)
            file = backend.get_file(config["uri"])
            # Set the retrieval finished time
            retrieval_finished_time = time.time()
            logger.info("File retrieved successfully. Size: %d bytes", len(file))
        except BackendInitException as e:
            return None, None, None, f"Failed to initialize backend: {str(e)}"
        except BackendException as e:
            # If retrieval fails, we should still delay if configured to do so
            return None, None, time.time(), f"Failed to retrieve file: {str(e)}"
        except Exception as e:
            # If retrieval fails for an unexpected reason, we should still delay if configured to do so
            return None, None, time.time(), f"Backend unexpectedly failed: {str(e)}"
    else:
        return None, None, None, "You must include either 'uri' or 'content' in the request body."

    detected_file_type = None
    if config.get("file_type"):
        # If a file type is provided, we use it directly instead of determining it from the file
        file_type = config["file_type"]
        logger.info("Attempting to use the provided file type: %s", file_type)
    else:
        # Determine the file's content type
        try:
            detected_file_type = file_type = Extractor.get_file_type(file)
        except Exception as e:
            return None, None, retrieval_finished_time, f"Failed to determine file type: {str(e)}"

    # Run extractor
    logger.info("Starting text extraction.")
    try:
        extractor = Extractor.get_extractor(file_type, config)
        text = extractor.extract(file)
    except ExtractorInitException as e:
        return None, detected_file_type, retrieval_finished_time, f"Failed to initialize text extractor: {str(e)}"
    except ExtractorException as e:
        return None, detected_file_type, retrieval_finished_time, f"Failed to extract text: {str(e)}"
    except Exception as e:
        return None, detected_file_type, retrieval_finished_time, f"Extractor unexpectedly failed: {str(e)}"

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
        return None, detected_file_type, retrieval_finished_time, None

    # Return the extracted text, file type, time that retrieval finished, and no error
    return text, detected_file_type, retrieval_finished_time, None


def handler(event: dict, context: Any) -> dict:
    """
    AWS Lambda handler function to process text extraction requests.
    This function initializes logging, retrieves configuration, and performs text extraction.
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
        index_id = config["id"]
        upload_url = config["upload_url"]
        if not any([i in config for i in ["uri", "content"]]):
            raise KeyError
    except KeyError:
        return lambda_response(400, "You must include 'id', 'upload_url', and either 'uri' or 'content' in the request body.")

    # Configure authorization
    authorization = None
    if config.get("auth"):
        try:
            authorization = configure_authorization(config["auth"])
        except Exception as e:
            return lambda_response(400, f"Failed to configure authorization: {str(e)}")

    sqs_group = config.get("sqs_group")
    retrieval_delay = config.get("retrieval_delay", 0)

    # Chunking configuration
    chunking = config.get("chunking", {})
    enable_chunking = chunking.get("enabled", False)
    chunk_size = chunking.get("chunk_size", 10000)
    chunk_overlap = chunking.get("chunk_overlap", 1000)

    # Embedding configuration
    embeddings = config.get("embedding", {})
    generate_embedding = embeddings.get("generate", False)
    embedding_model = embeddings.get("model", "amazon.titan-embed-text-v2:0")
    embedding_dimensions = embeddings.get("dimensions", 1024)
    normalize_embeddings = embeddings.get("normalize", True)

    try:
        # Perform text extraction
        text, file_type, retrieval_finished_time, error = extract_text(config, context)

        # Strip control characters and unneeded data out of the extracted text
        if text:
            text = clean_output(text)

        # If chunking is enabled, split text into chunks
        chunks = [text]  # Default to single chunk with full text
        if text and enable_chunking:
            logger.info("Chunking extracted text into chunks of size %d with overlap %d.", chunk_size, chunk_overlap)
            chunks = chunk_text(text, chunk_size, chunk_overlap)
            logger.info("Text chunked into %d chunks.", len(chunks))

        # If embeddings are enabled, generate embeddings for the text or chunks
        embeddings = [None] * len(chunks)  # Default to no embeddings
        if text and generate_embedding:
            client = boto3.client("bedrock-runtime")
            logger.info("Generating embeddings using model '%s' with %d dimensions.", embedding_model, embedding_dimensions)
            embeddings = [generate_embedding(
                client,
                chunk,
                embedding_model,
                embedding_dimensions,
                normalize_embeddings,
            ) for chunk in chunks]

        # Send results to eRegs for each chunk
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            send_results(
                index_id,
                upload_url,
                authorization,
                text=chunk,
                embedding=embedding,
                chunk_index=i,
                total_chunks=len(chunks),
                file_type=file_type,
                error=error,
            )

        if error:
            raise Exception(error)

        return lambda_response(200, "Text extraction completed successfully.")

    except Exception as e:
        if sqs_group:
            logger.error("An error occurred: %s", str(e))
            raise e
        return lambda_response(500, f"An error occurred: {str(e)}")

    finally:
        time_since_retrieval = time.time() - (retrieval_finished_time or 0)
        delay_time = retrieval_delay - time_since_retrieval
        remaining_time = (context.get_remaining_time_in_millis() / 1000) - 1  # Convert to seconds and subtract 1 for safety
        delay_time = delay_time if remaining_time > delay_time else remaining_time  # Don't delay more than the time left
        if retrieval_finished_time and time_since_retrieval < retrieval_delay:
            logger.info(
                "%sWaiting for %d seconds before finishing.",
                f"[Group: {sqs_group}] " if sqs_group else "",
                delay_time,
            )
            time.sleep(delay_time)

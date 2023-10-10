import sys
import json
import time
import requests

import magic

from .backends import (
    FileBackend,
    BackendInitException,
    BackendException,
)

from .extractors import (
    Extractor,
    ExtractorInitException,
)


def load_post_body(body):
    try:
        json.loads(body)
    except:
        return {}


def lambda_response(status_code, message):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": message}),
    }


def handler(event, context):
    get_params = event["queryStringParameters"]
    post_params = load_post_body(event["body"])

    # Retrieve required arguments
    try:
        resource_id = get_params["id"]
        uri = get_params["uri"]
    except KeyError:
        return lambda_response(400, "You must include 'id' and 'uri' in the query parameters.")

    # Initialize the file backend
    try:
        backend_type = get_params.get("backend", "web").lower()
        backend = FileBackend.get_backend(backend_type, get_params, post_params)
    except BackendInitException as e:
        return lambda_response(400, f"Failed to initialize backend: {str(e)}")

    # Retrieve the file
    try:
        file = backend.get_file(uri)
    except BackendException as e:
        return lambda_response(500, f"Failed to retrieve file: {str(e)}")

    # Determine the file's MIME type
    file_type = magic.from_buffer(
        file[0:min(len(file), 2048)],
        mime=True,
    )

    # Run extractor
    try:
        extractor = Extractor.get_extractor(file_type)
    except ExtractorInitException as e:
        return lambda_response(500, f"Failed to initialize text extractor: {str(e)}")

    # Return success code
    return lambda_response(200, "Function exited normally.")

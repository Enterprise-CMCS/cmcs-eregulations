import json

import magic

from .backends import (
    FileBackend,
    BackendInitException,
    BackendException,
)

from .extractors import (
    Extractor,
    ExtractorInitException,
    ExtractorException,
)


def load_post_body(body: str) -> dict:
    try:
        json.loads(body)
    except Exception:
        return {}


def lambda_response(status_code: int, message: str) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": message}),
    }


def handler(event: dict, context: dict) -> dict:
    get_params = event["queryStringParameters"]
    post_params = load_post_body(event["body"])

    # Retrieve required arguments
    try:
        get_params["id"]
        uri = get_params["uri"]
    except KeyError:
        return lambda_response(400, "You must include 'id' and 'uri' in the query parameters.")

    # Retrieve the file
    try:
        backend_type = get_params.get("backend", "web").lower()
        backend = FileBackend.get_backend(backend_type, get_params, post_params)
        file = backend.get_file(uri)
    except BackendInitException as e:
        return lambda_response(500, f"Failed to initialize backend: {str(e)}")
    except BackendException as e:
        return lambda_response(500, f"Failed to retrieve file: {str(e)}")
    except Exception as e:
        return lambda_response(500, f"Backend unexpectedly failed: {str(e)}")

    # Determine the file's MIME type
    # Magic docs recommend using first 2048 bytes of the file for most accurate type detection
    try:
        file_type = magic.from_buffer(
            file[0:min(len(file), 2048)],
            mime=True,
        )
    except Exception as e:
        return lambda_response(500, f"Failed to determine file type: {str(e)}")

    # Run extractor
    try:
        extractor = Extractor.get_extractor(file_type)
        extractor.extract(file)
    except ExtractorInitException as e:
        return lambda_response(500, f"Failed to initialize text extractor: {str(e)}")
    except ExtractorException as e:
        return lambda_response(500, f"Failed to extract text: {str(e)}")
    except Exception as e:
        return lambda_response(500, f"Extractor unexpectedly failed: {str(e)}")

    # Return success code
    return lambda_response(200, "Function exited normally.")

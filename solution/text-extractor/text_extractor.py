import json

import magic
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
    post_params = load_post_body(event["body"])

    # Retrieve required arguments
    try:
        resource_id = post_params["id"]
        uri = post_params["uri"]
        post_url = post_params["post_url"]
        post_username = post_params.get("post_username")
        post_password = post_params.get("post_password")
    except KeyError:
        return lambda_response(400, "You must include 'id', 'uri', and 'post_url' in the query parameters.")

    # Retrieve the file
    try:
        backend_type = post_params.get("backend", "web").lower()
        backend = FileBackend.get_backend(backend_type, post_params)
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
        file_type = magic.from_buffer(file[:2048], mime=True)
    except Exception as e:
        return lambda_response(500, f"Failed to determine file type: {str(e)}")

    # Run extractor
    try:
        extractor = Extractor.get_extractor(file_type)
        text = extractor.extract(file)
    except ExtractorInitException as e:
        return lambda_response(500, f"Failed to initialize text extractor: {str(e)}")
    except ExtractorException as e:
        return lambda_response(500, f"Failed to extract text: {str(e)}")
    except Exception as e:
        return lambda_response(500, f"Extractor unexpectedly failed: {str(e)}")

    # Send result to eRegs
    try:
        requests.post(
            post_url,
            auth=(post_username, post_password) if post_username and post_password else None,
            data=json.dumps({
                "id": resource_id,
                "text": text,
            }),
            timeout=60,
        )
    except requests.exceptions.RequestException as e:
        return lambda_response(500, f"Failed to POST results: {str(e)}")
    except Exception as e:
        return lambda_response(500, f"POST unexpectedly failed: {str(e)}")

    # Return success code
    return lambda_response(200, "Function exited normally.")

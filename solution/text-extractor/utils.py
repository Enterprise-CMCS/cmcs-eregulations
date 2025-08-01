import json
import logging
import re
import unicodedata
import base64
import os

import boto3
from botocore.exceptions import ClientError
import requests

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def lambda_response(status_code: int, message: str) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": message}),
    }


def get_config(event: dict) -> dict:
    logger.info("Retrieving Lambda event dictionary.")

    # Handle invocation from SQS (only one record at a time)
    if "Records" in event and event["Records"]:
        logger.debug("Found a 'Records' key in the event, assuming SQS invocation.")
        record = event["Records"][0]
        config = json.loads(record["body"])
        config["sqs_group"] = record.get("attributes", {}).get("MessageGroupId")
        return config

    # Handle API Gateway invocation
    if "body" in event and event["body"]:
        logger.debug("Found a 'body' key in the event, assuming API Gateway invocation.")
        return json.loads(event["body"])

    # Handle direct invocation via boto3 etc.
    logger.debug("No 'body' key present in the event, assuming direct AWS invocation.")
    return event


def clean_output(text: str) -> str:
    text = "".join(ch if not unicodedata.category(ch).lower().startswith("c") else " " for ch in text)
    return re.sub(r"\s+", " ", text).strip()


def get_secret_from_aws(secret_name: str) -> dict:
    logger.info("Retrieving secret from AWS Secrets Manager.")

    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.error("Failed to retrieve secret from AWS Secrets Manager: %s", str(e))
        raise Exception(f"failed to retrieve secret from AWS Secrets Manager: {str(e)}")

    return json.loads(response["SecretString"])


def configure_authorization(auth: dict) -> str:
    auth_type = auth["type"].lower().strip()

    if auth_type == "token":
        token = auth["token"]
        return f"Bearer {token}"

    if auth_type in ["basic", "basic-env"]:
        username, password = (
            (auth["username"], auth["password"])
            if auth_type == "basic" else
            (os.environ[auth["username"]], os.environ[auth["password"]])
        )
        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {token}"

    if auth_type in ["basic-secretsmanager", "basic-secretsmanager-env"]:
        secret_name = (
            auth["secret_name"]
            if auth_type == "basic-secretsmanager" else
            os.environ[auth["secret_name"]]
        )
        secret = get_secret_from_aws(secret_name)
        username = secret[auth["username_key"]]
        password = secret[auth["password_key"]]
        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {token}"

    raise Exception(f"'{auth_type}' is an unsupported authorization type")


def send_results(resource_id: int, upload_url: str, auth: str, **kwargs) -> None:
    """
    Send extracted text and related data to the eRegs service via a PATCH request.

    Args:
        resource_id (int): The ID of the resource to update.
        upload_url (str): The URL endpoint for the PATCH request.
        auth (str): Authorization token for the request headers, or None if not required.
        **kwargs: Additional data to include in the request payload (e.g., "text", "file_type", "error").

    Raises:
        Exception: If the PATCH request fails or an unexpected error occurs.
    """

    # Prepare the data to send
    error = None
    headers = {'Authorization': auth} if auth else {}
    data = {"id": resource_id, **{k: v for k, v in kwargs.items() if v}}

    # Send the PATCH request to eRegs
    logger.info("Sending results to eRegs at %s for resource ID %d.", upload_url, resource_id)
    try:
        response = requests.patch(
            upload_url,
            headers=headers,
            json=data,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if hasattr(e, "response") and hasattr(e.response, "text") and e.response.text:
            error = f"Failed to send results to eRegs with status code {e.response.status_code}: {e.response.text}"
        else:
            error = f"Failed to send results to eRegs: {str(e)}"
    except Exception as e:
        error = f"Unexpected error while sending results to eRegs: {str(e)}"
    finally:
        additional_error_text = kwargs.get("error", "")
        if additional_error_text:
            additional_error_text += f". An additional error occurred while extracting text: {additional_error_text}."
        if error:
            error = f"{error}{additional_error_text}"
            logger.error(error)
            raise Exception(error)

import json
import logging
import re
import unicodedata
import base64
import os

import boto3
from botocore.exceptions import ClientError

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
        logger.debug("Found truthy 'Records' key in event, assuming SQS invocation.")
        logger.info(json.dumps(event["Records"]))
        config = json.loads(event["Records"][0]["body"])
        # For SQS, we need to raise an exception during a failure event to ensure the message is not deleted from the queue
        config["raise_on_failure"] = True
        return config

    # Handle API Gateway invocation
    if "body" in event and event["body"]:
        logger.debug("Found truthy 'body' key in event, assuming API Gateway invocation.")
        config = json.loads(event["body"])
        config["raise_on_failure"] = False
        return config

    # Handle direct invocation via boto3 etc.
    logger.debug("No 'body' key present in event, assuming direct AWS invocation.")
    event["raise_on_failure"] = False
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

import json
import logging
import re
import unicodedata
import base64
import os

logger = logging.getLogger(__name__)


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


def get_config(event: dict) -> dict:
    logger.info("Retrieving Lambda event dictionary.")
    if "Records" in event and event["Records"]:
        # Invoked from SQS (we handle only one message at a time)
        raise Exception(event["Records"][0]["body"])
    if "body" not in event:
        # Assume we are invoked directly
        logger.debug("No 'body' key present in event, assuming direct invocation.")
        return event
    else:
        try:
            return json.loads(event["body"])
        except Exception as e:
            raise Exception(f"unable to parse body as JSON: {str(e)}")


def clean_output(text: str) -> str:
    text = "".join(ch if not unicodedata.category(ch).lower().startswith("c") else " " for ch in text)
    return re.sub(r"\s+", " ", text).strip()


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

    raise Exception(f"'{auth_type}' is an unsupported authorization type")

import json
import logging
import re
import unicodedata

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

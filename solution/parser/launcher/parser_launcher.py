import os
import logging
import boto3
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info("Retrieving secrets from AWS Secrets Manager.")

    try:
        secret_name = os.environ["SECRET_NAME"]
        secretsmanager_client = boto3.client('secretsmanager')
        response = secretsmanager_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        # Payload to send to the invoked Lambda functions
        payload = {
            "username": secret["username"],
            "password": secret["password"],
        }
    except Exception as e:
        logger.error(f"Failed to retrieve secret: {str(e)}")
        raise


    lambda_client = boto3.client('lambda')
    ecfr_parser_arn = os.environ['ECFR_PARSER_ARN']
    fr_parser_arn = os.environ['FR_PARSER_ARN']

    logger.info("Invoking the eCFR parser asynchronously.")

    # Invoke the eCFR parser
    lambda_client.invoke(
        FunctionName=ecfr_parser_arn,
        InvocationType='Event',  # Asynchronous invocation
        Payload=json.dumps(payload),
    )

    logger.info("Invoking the FR parser asynchronously.")

    # Invoke the FR parser
    lambda_client.invoke(
        FunctionName=fr_parser_arn,
        InvocationType='Event',  # Asynchronous invocation
        Payload=json.dumps(payload),
    )

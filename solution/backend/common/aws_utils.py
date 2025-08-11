import json

import boto3
import requests
from django.conf import settings


def get_aws_client(service_name, region_name="us-east-1"):
    """
    Create and return an AWS service client.

    :param service_name: The name of the AWS service (e.g., 's3', 'ec2').
    :param region_name: The AWS region to connect to (optional).
    :return: A boto3 client for the specified service.
    """
    if settings.USE_AWS_TOKEN:
        return boto3.client(
            service_name,
            aws_access_key_id=settings.S3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_AWS_SECRET_ACCESS_KEY,
            region_name=region_name,
        )
    else:
        return boto3.client(service_name, region_name=region_name)


def invoke_lambda_via_http(batch, url):
    success = 0
    fail = []

    for request in batch:
        try:
            resp = requests.post(
                url,
                data=json.dumps(request),
                headers={"Content-Type": "application/json"},
                timeout=60,
            )
            if resp.status_code != requests.codes.OK and hasattr(resp, "text") and resp.text:
                raise RuntimeError(f"Error invoking external service: {resp.status_code} - {resp.text}")
            resp.raise_for_status()
            success += 1
        except Exception as e:
            fail.append({
                "id": request.get("id", "unknown"),
                "reason": str(e)
            })

    return success, fail


def invoke_lambda_via_sqs(batch, client, url, get_message_group_id_func=None):
    """
    Send a batch of requests to an AWS SQS queue.

    :param batch: List of requests to send.
    :param client: Boto3 SQS client.
    :param url: The SQS queue URL.
    :param get_message_group_id_func: Optional function to determine the message group ID.
    :return: Tuple of success count and list of failed requests.
    """

    entries = [{
        **{"Id": str(i["id"]), "MessageBody": json.dumps(i)},
        **({"MessageGroupId": get_message_group_id_func(i)} if get_message_group_id_func else {})
    } for i in batch]

    try:
        resp = client.send_message_batch(
            QueueUrl=url,
            Entries=entries,
        )
        success = len(resp.get("Successful", []))
        fail = [{
            "id": int(i["Id"]),
            "reason": f"Received code {i['Code']}: {i['Message']}",
        } for i in resp.get("Failed", [])]
    except Exception as e:
        success = 0
        fail = [{
            "id": i["id"],
            "reason": str(e),
        } for i in batch]

    return success, fail


def invoke_lambda_via_lambda(batch, client, arn):
    """
    Invoke an AWS Lambda function with a batch of requests.

    :param batch: List of requests to send.
    :param client: Boto3 Lambda client.
    :param arn: The ARN of the Lambda function.
    :return: Tuple of success count and list of failed requests.
    """

    success = 0
    fail = []

    for request in batch:
        try:
            client.invoke(
                FunctionName=arn,
                InvocationType="Event",
                Payload=json.dumps(request),
            )
            success += 1
        except Exception as e:
            fail.append({
                "id": request["id"],
                "reason": str(e),
            })

    return success, fail

import json

import boto3
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from resources.models import FederalRegisterLink

_LOCAL_TEXT_EXTRACTOR_URL = "http://host.docker.internal:8001/"
_LOCAL_EREGS_URL = "http://host.docker.internal:8000"


# Establishes an AWS client.
#
# client_type: the boto3-recognized AWS resource to create a client for.
def establish_client(client_type):
    if settings.USE_AWS_TOKEN:
        return boto3.client(
            client_type,
            aws_access_key_id=settings.S3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_AWS_SECRET_ACCESS_KEY,
            region_name="us-east-1",
        )
    else:
        return boto3.client(client_type, region_name="us-east-1")


def _extract_via_http(batch, client):
    success = 0
    fail = []

    for request in batch:
        try:
            resp = requests.post(
                _LOCAL_TEXT_EXTRACTOR_URL,
                data=json.dumps(request),
                timeout=60,
            )
            if resp.status_code != requests.codes.OK and hasattr(resp, "text") and resp.text:
                raise RuntimeError(f"POST failed with {resp.status_code}: {resp.text}")
            resp.raise_for_status()
            success += 1
        except Exception as e:
            fail.append({
                "id": request["id"],
                "reason": str(e),
            })

    return success, fail


def _extract_via_sqs(batch, client):
    entries = [{
        "Id": str(i["id"]),
        "MessageBody": json.dumps(i),
    } for i in batch]

    try:
        resp = client.send_message_batch(
            QueueUrl=settings.TEXT_EXTRACTOR_QUEUE_URL,
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


def _extract_via_lambda(batch, client):
    success = 0
    fail = []

    for request in batch:
        try:
            client.invoke(
                FunctionName=settings.TEXT_EXTRACTOR_ARN,
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


# Internal function to compute the 2 keys needed for text-extractor requests: "uri" and "backend".
def _get_resource_keys(resource):
    if hasattr(resource, "key"):
        return {
            "uri": resource.key,
            "backend": "s3",
        }
    return {
        "uri": resource.extract_url or resource.url,
        "backend": "web",
    }


# Run the text extractor for the given resources.
# For SQS, requests are batched by groups of 10.
#
# Note the choice of execution path based on the three Django settings:
#   - USE_LOCAL_TEXT_EXTRACTOR: if true will use the local dockerized text extractor instead of the AWS client.
#   - TEXT_EXTRACTOR_QUEUE_URL: if set will use the SQS queue instead of invoking the Lambda directly.
#   - TEXT_EXTRACTOR_ARN: if the above is not set and this is, will invoke the Lamba directly.
# If none of these are set, ImproperlyConfigured is raised.
#
# Arguments:
# request: the Django Request object that caused this call to occur.
# resources: a list containing subclasses of AbstractResource to process.
#
# Returns:
# Two values; successes by count, and failures by dict: {"id": x, "reason": "y"}.
# Note that a successful return does not necessarily indicate a successful extraction;
# Check text-extractor logs to verify extraction.
def call_text_extractor(request, resources):
    requests = [{**{
        "id": i.pk,
        "ignore_robots_txt": isinstance(i, FederalRegisterLink),
        "upload_url": (
            f"{_LOCAL_EREGS_URL}{reverse('content', args=[i.pk])}"
            if settings.USE_LOCAL_TEXT_EXTRACTOR else
            request.build_absolute_uri(reverse("content", args=[i.pk]))
        ),
        "auth": {
            "type": "basic",
            "username": settings.HTTP_AUTH_USER,
            "password": settings.HTTP_AUTH_PASSWORD,
        } if settings.USE_LOCAL_TEXT_EXTRACTOR else {
            "type": "basic-env",
            "username": "HTTP_AUTH_USER",
            "password": "HTTP_AUTH_PASSWORD",
        },
        "aws": {
            "aws_access_key_id": settings.S3_AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.S3_AWS_SECRET_ACCESS_KEY,
            "aws_storage_bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
            "use_lambda": False,
            "aws_region": "us-east-1",
        } if settings.USE_LOCAL_TEXT_EXTRACTOR else {
            "use_lambda": True,
            "aws_storage_bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
        },
    }, **_get_resource_keys(i)} for i in resources]

    succeed_count = 0
    failures = [{
        "id": i["id"],
        "reason": "The URI field is blank for this resource.",
    } for i in requests if not i["uri"].strip()]
    requests = [i for i in requests if i["uri"].strip()]

    if settings.USE_LOCAL_TEXT_EXTRACTOR:
        extract_function = _extract_via_http
        client = None
    elif settings.TEXT_EXTRACTOR_QUEUE_URL:
        extract_function = _extract_via_sqs
        client = establish_client("sqs")
    elif settings.TEXT_EXTRACTOR_ARN:
        extract_function = _extract_via_lambda
        client = establish_client("lambda")
    else:
        raise ImproperlyConfigured("The text extractor destination is not configured.")

    for batch in [requests[i:i + 10] for i in range(0, len(requests), 10)]:
        success, fail = extract_function(batch, client)
        succeed_count += success
        failures += fail

    return succeed_count, failures

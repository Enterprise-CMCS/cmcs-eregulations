# Functions and mixins that are exportable to other apps may go here

import json

import boto3
import requests
from django.conf import settings
from django.core.exceptions import BadRequest, ImproperlyConfigured
from django.db.models import Q
from django.urls import reverse

from resources.models import FederalRegisterLink


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


# Returns True if x is an integer, False otherwise.
def is_int(x):
    try:
        _ = int(x)
        return True
    except ValueError:
        return False


# Generates an OR'd together Q query of all citations passed in via the "citations" argument.
# The results of this function may be passed directly into a Django 'filter' call or manipulated like any Q object.
#
# For example, pass in ["42.433.1", "42.433.2"] and get:
#     (Q(title=42) & Q(part=433) & Q(section_id=1)) | (Q(title=42) & Q(part=433) & Q(section_id=2))
#
# citations: list of citation strings
# filter_prefix: query prefix for nested citations (e.g. "cfr_citations__" or "resources__cfr_citations__")
# max_depth: restrict searching to titles (=1) or parts (=2)
def get_citation_filter(citations, filter_prefix, max_depth=100):
    queries = []
    for loc in citations:
        split = loc.split(".")
        length = len(split)

        if length < 1 or \
                (length >= 1 and not is_int(split[0])) or \
                (length >= 2 and (not is_int(split[0]) or not is_int(split[1]))):
            raise BadRequest(f"\"{loc}\" is not a valid title, part, section, or subpart!")

        q = Q(**{f"{filter_prefix}title": split[0]})
        if length > 1:
            if max_depth < 2:
                raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles.")
            q &= Q(**{f"{filter_prefix}part": split[1]})
            if length > 2:
                if max_depth < 3:
                    raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles and parts.")
                q &= (
                    Q(**{f"{filter_prefix}section__section_id": split[2]})
                    if is_int(split[2])
                    else (
                            Q(**{f"{filter_prefix}subpart__subpart_id": split[2]}) |
                            Q(**{f"{filter_prefix}section__parent__subpart_id": split[2]})
                    )
                )

        queries.append(q)

    q_obj = Q()
    for q in queries:
        q_obj |= q
    return q_obj


# Convert a boolean value encoded as a string to a bool.
#
# 'true', 't', 'y', 'yes', '1' all return True.
# 'false', 'f', 'n', 'no', '0' all return False.
#
# value: the string to convert to a bool (case insensitive)
# default: the default to return if 'value' is None
def string_to_bool(value, default):
    if not value:
        return default
    value = value.lower().strip()
    if value in ("true", "t", "y", "yes", "1"):
        return True
    elif value in ("false", "f", "n", "no", "0"):
        return False
    raise ValueError(f"The value '{value}' cannot be converted to a bool.")


# Run the text extractor for the given resource.
#
# Note the choice of execution path based on the three Django settings:
#   - USE_LOCAL_TEXT_EXTRACTOR: if true will use the local dockerized text extractor instead of the AWS client.
#   - TEXT_EXTRACTOR_QUEUE_URL: if set will use the SQS queue instead of invoking the Lambda directly.
#   - TEXT_EXTRACTOR_ARN: if the above is not set and this is, will invoke the Lamba directly.
# If none of these are set properly, ImproperlyConfigured is raised.
#
# Arguments:
# request: the Django Request object that caused this call to occur.
# resource: any subclass of AbstractResource.
#
# Does not return a value on success, but raises on failure.
# Note that a successful return does not necessarily indicate a successful extraction.
# Check text-extractor logs to verify extraction.
def call_text_extractor(request, resource):
    update_content_url = reverse("content", args=[resource.pk])
    upload_url = (
        request.build_absolute_uri(update_content_url)
        if not settings.USE_LOCAL_TEXT_EXTRACTOR else
        f"http://host.docker.internal:8000{update_content_url}"
    )

    request = {
        "id": resource.pk,
        "ignore_robots_txt": isinstance(resource, FederalRegisterLink),
        "upload_url": upload_url,
        "auth": {
            "type": "basic-env",
            "username": "HTTP_AUTH_USER",
            "password": "HTTP_AUTH_PASSWORD",
        } if not settings.USE_LOCAL_TEXT_EXTRACTOR else {
            "type": "basic",
            "username": settings.HTTP_AUTH_USER,
            "password": settings.HTTP_AUTH_PASSWORD,
        },
        "aws": {
            "aws_access_key_id": settings.S3_AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.S3_AWS_SECRET_ACCESS_KEY,
            "aws_storage_bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
            "use_lambda": False,
            "aws_region": "us-east-1",
        } if not settings.USE_LOCAL_TEXT_EXTRACTOR else {
            "use_lambda": True,
            "aws_storage_bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
        }
    }

    try:
        request["uri"] = resource.key
        request["backend"] = "s3"
    except AttributeError:
        request["uri"] = resource.extract_url or resource.url
        request["backend"] = "web"

    request = json.dumps(request)

    if settings.USE_LOCAL_TEXT_EXTRACTOR:
        docker_url = "http://host.docker.internal:8001/"
        resp = requests.post(
            docker_url,
            data=request,
            timeout=60,
        )
        if resp.status_code != requests.codes.OK and hasattr(resp, "text") and resp.text:
            raise RuntimeError(f"POST failed with {resp.status_code}: {resp.text}")
        resp.raise_for_status()
    elif settings.TEXT_EXTRACTOR_QUEUE_URL:
        sqs_client = establish_client("sqs")
        sqs_client.send_message(
            QueueUrl=settings.TEXT_EXTRACTOR_QUEUE_URL,
            MessageBody=request,
        )
    elif settings.TEXT_EXTRACTOR_ARN:
        lambda_client = establish_client("lambda")
        lambda_client.invoke(
            FunctionName=settings.TEXT_EXTRACTOR_ARN,
            InvocationType="Event",
            Payload=request,
        )
    else:
        raise ImproperlyConfigured("The text extractor destination is not configured.")

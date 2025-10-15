import base64
import json
import unicodedata
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.urls import reverse

from common.aws import establish_client
from regcore.models import Part
from resources.models import (
    AbstractResource,
    FederalRegisterLink,
    ResourcesConfiguration,
)

from .models import (
    ContentIndex,
    IndexedRegulationText,
)

_LOCAL_TEXT_EXTRACTOR_URL = "http://host.docker.internal:8001/"
_LOCAL_EREGS_URL = "http://host.docker.internal:8000"


# Remove control characters from a string
#
# text: str - the text to remove control characters from
# returns: str - the text with control characters removed
def remove_control_characters(text: str) -> str:
    return "".join(ch if not unicodedata.category(ch).lower().startswith("c") else " " for ch in text).strip()


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


def _get_message_group_id(request):
    backend = request.get("backend")
    if backend == "s3":
        # Each S3 request belongs to a new group to allow unrestricted parallel processing
        return f"s3:{request['uri']}"
    elif backend == "web":
        # Web requests are grouped by domain name to avoid any parallel requests to the same server
        # Requests to different domains can be processed in parallel without issue
        hostname = urlparse(request["uri"]).hostname or "default"
        domain_name = ".".join(hostname.split(".")[-2:])
        return f"web:{domain_name}"
    # Fallback for unknown backends
    return f"{backend}:default"


def _extract_via_sqs(batch, client):
    entries = [{
        "Id": str(i["id"]),
        "MessageBody": json.dumps(i),
        "MessageGroupId": _get_message_group_id(i),
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
# kwargs accepted:
#  - user_agent_override_list: a list of dicts with "domain" and "user_agent" keys.
#  - default_user_agent_override: a string to use as the default user agent if no override is found.
#  - retrieval_delay: an integer representing the delay time in seconds for the request.
def _get_resource_keys(resource, **kwargs):
    if hasattr(resource, "key"):
        return {
            "uri": resource.key,
            "backend": "s3",
        }

    # Determine if we should override the user agent for this resource.
    user_agent_override_list = kwargs.get("user_agent_override_list", [])
    default_user_agent_override = kwargs.get("default_user_agent_override", "")
    url = resource.extract_url or resource.url
    domain = urlparse(url).hostname or ""
    user_agent = None
    for item in user_agent_override_list:
        if item["domain"] == domain or domain.endswith('.' + item["domain"]):
            user_agent = item["user_agent"] or default_user_agent_override
            break

    return {
        "uri": url,
        "backend": "web",
        "retrieval_delay": kwargs.get("retrieval_delay", 0),
        "user_agent": user_agent,
    }


# Determines if the robots.txt should be ignored for the given resource.
# Currently, this is true for all FederalRegisterLink resources and resources that have URLs in the allow list.
def _should_ignore_robots_txt(resource, allow_list):
    if isinstance(resource, FederalRegisterLink):
        return True

    url = (resource.extract_url or resource.url).strip().lower()
    resource_domain = urlparse(url).hostname or ""

    for pattern in allow_list:
        # Exact URL match
        if pattern.startswith('http://') or pattern.startswith('https://'):
            if url == pattern:
                return True
        # Domain match (e.g. 'example.com' will match 'https://example.com/path' and 'http://www.example.com/path')
        elif not pattern.startswith('http'):  # Most likely not an exact URL
            if resource_domain == pattern or resource_domain.endswith('.' + pattern):
                return True

    # If no match found, do not ignore robots.txt
    return False


# Run the text extractor for the given resources.
# For SQS, requests are batched by groups of 10.
#
# Note the choice of execution path based on the three Django settings:
#   - USE_LOCAL_TEXT_EXTRACTOR: if true will use the local dockerized text extractor instead of the AWS client.
#   - TEXT_EXTRACTOR_QUEUE_URL: if set will use the SQS queue instead of invoking the Lambda directly.
#   - TEXT_EXTRACTOR_ARN: if the above is not set and this is, will invoke the Lamba directly.
# If none of these are set, extraction will fail for all resources.
#
# Arguments:
# request: the Django Request object that caused this call to occur.
# resources: a list containing subclasses of AbstractResource to process.
#
# Returns:
# Two values; successes by count, and failures by dict: {"id": x, "reason": "y"}.
# Note that a successful return does not necessarily indicate a successful extraction;
# Check text-extractor logs to verify extraction.
def call_text_extractor_for_resources(request, resources):
    # Blank the error field for all resources before processing
    AbstractResource.objects.filter(pk__in=[i.pk for i in resources]).update(extraction_error="")

    # Retrieve relevant configuration from the ResourcesConfiguration solo model
    config = ResourcesConfiguration.get_solo()
    allow_list = config.robots_txt_allow_list
    extraction_delay_time = config.extraction_delay_time
    default_user_agent_override = config.default_user_agent_override
    user_agent_override_list = config.user_agent_override_list

    requests = [{**{
        "id": i.pk,
        "ignore_robots_txt": _should_ignore_robots_txt(i, allow_list),
        "file_type": i.file_type or None,
        "upload_url": (
            f"{_LOCAL_EREGS_URL}{reverse('resource_chunk_update', args=[i.pk])}"
            if settings.USE_LOCAL_TEXT_EXTRACTOR else
            request.build_absolute_uri(reverse("resource_chunk_update", args=[i.pk]))
        ),
        "auth": {
            "type": "basic",
            "username": settings.HTTP_AUTH_USER,
            "password": settings.HTTP_AUTH_PASSWORD,
        } if settings.USE_LOCAL_TEXT_EXTRACTOR else {
            "type": "basic-secretsmanager-env",
            "secret_name": "SECRET_NAME",
            "username_key": "username",
            "password_key": "password",
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
    }, **_get_resource_keys(
        i,
        user_agent_override_list=user_agent_override_list,
        default_user_agent_override=default_user_agent_override,
        retrieval_delay=extraction_delay_time,
    )} for i in resources]

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
        failures += [{
            "id": i["id"],
            "reason": "The text extractor destination is not configured.",
        } for i in requests]
        requests = []

    for batch in [requests[i:i + 10] for i in range(0, len(requests), 10)]:
        success, fail = extract_function(batch, client)
        succeed_count += success
        failures += fail

    return succeed_count, failures


def index_part_node(part, piece, indices, contents, parent=None, subpart_id="", subpart_title=""):
    try:
        node_type = piece.get("node_type", "").lower()
        part_number, node_id = {
            "section": (0, 1),
            "appendix": (6, 3),
        }[node_type]

        label = piece["label"]
        part_number = int(label[part_number])
        node_id = remove_control_characters(label[node_id])

        content = piece.get("title", piece.get("text", ""))
        children = piece.pop("children", []) or []
        for child in children:
            content += child.get("text", "") + child.get("content", "")

        contents.append(remove_control_characters(content))
        indices.append(IndexedRegulationText(
            part=part,
            title=part.title,
            date=part.date,
            part_title=remove_control_characters(part.document["title"]),
            part_number=part_number,
            subpart_title=remove_control_characters(subpart_title),
            subpart_id=subpart_id,
            node_type=node_type,
            node_id=node_id,
            node_title=remove_control_characters(piece["title"]),
        ))

    except Exception:
        children = piece.pop("children", []) or []
        subpart_id = piece.get("label", [])[0] if piece.get("node_type", "").lower() == "subpart" else ""
        subpart_title = piece.get("title", "") if piece.get("node_type", "").lower() == "subpart" else ""
        for child in children:
            index_part_node(part, child, indices, contents, parent=piece, subpart_id=subpart_id, subpart_title=subpart_title)

    return indices, contents


# Run the text extractor for the given Part instances.
# For SQS, requests are batched by groups of 10.
#
# Note the choice of execution path based on the three Django settings:
#   - USE_LOCAL_TEXT_EXTRACTOR: if true will use the local dockerized text extractor instead of the AWS client.
#   - TEXT_EXTRACTOR_QUEUE_URL: if set will use the SQS queue instead of invoking the Lambda directly.
#   - TEXT_EXTRACTOR_ARN: if the above is not set and this is, will invoke the Lamba directly.
# If none of these are set, extraction will fail for all Part instances.
#
# Arguments:
# request: the Django Request object that caused this call to occur.
# parts: a list containing Part instances to process.
#
# Returns:
# Two values; successes by count, and failures by dict: {"id": x, "reason": "y"}.
# Note that a successful return does not necessarily indicate a successful extraction;
# Check text-extractor logs to verify extraction.
def call_text_extractor_for_reg_text(request, parts):
    # Blank the error field for all IndexedRegulationText instances before processing
    IndexedRegulationText.objects.filter(pk__in=[i.pk for i in parts]).update(extraction_error="")

    # Delete all previously indexed text for the given parts, including previous versions
    affected_indices = IndexedRegulationText.objects.filter(
        part__title__in=[i.title for i in parts],
        part__name__in=[i.name for i in parts],
    )
    ContentIndex.objects.filter(reg_text__in=affected_indices).delete()

    # Only index the latest version of each part
    parts = Part.objects.filter(
        title__in=[i.title for i in parts],
        name__in=[i.name for i in parts],
    ).order_by("title", "name", "-date").distinct("title", "name")

    # Build the IndexedRegulationText instances and the text contents to be indexed
    indices, contents = [], []
    for part in parts:
        i, c = index_part_node(part, part.document, [], [])
        indices += i
        contents += c

    # Create the IndexedRegulationText instances in bulk and encode the contents
    indices = IndexedRegulationText.objects.bulk_create(indices)
    contents = [base64.b64encode(i.encode("utf-8")).decode("utf-8") for i in contents]

    # Build the requests for the text extractor
    requests = [{
        "id": index.pk,
        "ignore_robots_txt": True,
        "content": content,
        "upload_url": (
            f"{_LOCAL_EREGS_URL}{reverse("reg_text_chunk_update", args=[index.pk])}"
            if settings.USE_LOCAL_TEXT_EXTRACTOR else
            request.build_absolute_uri(reverse("reg_text_chunk_update", args=[index.pk]))
        ),
        "auth": {
            "type": "basic",
            "username": settings.HTTP_AUTH_USER,
            "password": settings.HTTP_AUTH_PASSWORD,
        } if settings.USE_LOCAL_TEXT_EXTRACTOR else {
            "type": "basic-secretsmanager-env",
            "secret_name": "SECRET_NAME",
            "username_key": "username",
            "password_key": "password",
        },
    } for index, content in zip(indices, contents)]

    succeed_count = 0
    failures = []

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
        failures += [{
            "id": i["id"],
            "reason": "The text extractor destination is not configured.",
        } for i in requests]
        requests = []

    for batch in [requests[i:i + 10] for i in range(0, len(requests), 10)]:
        success, fail = extract_function(batch, client)
        succeed_count += success
        failures += fail

    return succeed_count, failures

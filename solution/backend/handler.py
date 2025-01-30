#!/usr/bin/env python

import base64
import io
import json
import os
import sys
from urllib.parse import urlencode, unquote, unquote_plus

from werkzeug.datastructures import Headers, iter_multi_items
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.wrappers import Response

from django.core.wsgi import get_wsgi_application


# List of MIME types that should not be base64 encoded. MIME types within `text/*`
# are included by default.
TEXT_MIME_TYPES = [
    "application/json",
    "application/javascript",
    "application/xml",
    "application/vnd.api+json",
    "image/svg+xml",
]


def get_script_name(headers, request_context):
    stage = os.environ.get("STAGE_ENV") or request_context.get("stage")
    if stage and "amazonaws.com" in headers.get("Host", ""):
        return f"/{stage}"
    return ""


def get_body_bytes(event, body):
    if event.get("isBase64Encoded", False):
        return base64.b64decode(body)
    elif isinstance(body, str):
        return body.encode("utf-8")
    return body


def setup_environment(headers, environment):
    for key, value in environment.items():
        if isinstance(value, str):
            environment[key] = value.encode("utf-8").decode("latin1", "replace")
    for key, value in headers.items():
        key = "HTTP_" + key.replace("-", "_").upper()
        if key not in ("HTTP_CONTENT_TYPE", "HTTP_CONTENT_LENGTH"):
            environment[key] = value
    return environment


def all_casings(input_string):
    if not input_string:
        yield ""
    else:
        first = input_string[:1]
        if first.lower() == first.upper():
            for sub_casing in all_casings(input_string[1:]):
                yield first + sub_casing
        else:
            for sub_casing in all_casings(input_string[1:]):
                yield first.lower() + sub_casing
                yield first.upper() + sub_casing


def split_headers(headers):
    new_headers = {}
    for key in headers.keys():
        values = headers.get_all(key)
        if len(values) > 1:
            for value, casing in zip(values, all_casings(key)):
                new_headers[casing] = value
        elif len(values) == 1:
            new_headers[key] = values[0]
    return new_headers


def group_headers(headers):
    new_headers = {}
    for key in headers.keys():
        new_headers[key] = headers.get_all(key)
    return new_headers


def generate_response(response, event):
    returndict = {"statusCode": response.status_code}

    if "multiValueHeaders" in event and event["multiValueHeaders"]:
        returndict["multiValueHeaders"] = group_headers(response.headers)
    else:
        returndict["headers"] = split_headers(response.headers)
    
    if response.data:
        mimetype = response.mimetype or "text/plain"
        if all([
            mimetype.startswith("text/") or mimetype in TEXT_MIME_TYPES,
            not response.headers.get("Content-Encoding", ""),
        ]):
            returndict["body"] = response.get_data(as_text=True)
            returndict["isBase64Encoded"] = False
        else:
            returndict["body"] = base64.b64encode(response.data).decode("utf-8")
            returndict["isBase64Encoded"] = True
    
    return returndict


def encode_query_string(event):
    params = event.get("multiValueQueryStringParameters") or event.get("queryStringParameters") or event.get("query") or ""
    return urlencode(params, doseq=True)


def handler(event, context):
    if "multiValueHeaders" in event and event["multiValueHeaders"]:
        headers = Headers(event["multiValueHeaders"])
    else:
        headers = Headers(event["headers"])
    
    script_name = get_script_name(headers, event.get("requestContext", {}))
    path_info = event["path"]
    body = get_body_bytes(event, event.get("body") or "")

    environment = setup_environment(headers, {
        "CONTENT_LENGTH": str(len(body)),
        "CONTENT_TYPE": headers.get("Content-Type", ""),
        "PATH_INFO": unquote(path_info),
        "QUERY_STRING": encode_query_string(event),
        "REMOTE_ADDR": event.get("requestContext", {}).get("identity", {}).get("sourceIp", ""),
        "REMOTE_USER": (event.get("requestContext", {}).get("authorizer") or {}),
        "REQUEST_METHOD": event.get("httpMethod", {}),
        "SCRIPT_NAME": script_name,
        "SERVER_NAME": headers.get("Host", "lambda"),
        "SERVER_PORT": headers.get("X-Forwarded-Port", "443"),
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.errors": sys.stderr,
        "wsgi.input": io.BytesIO(body),
        "wsgi.multiprocess": False,
        "wsgi.multithread": False,
        "wsgi.run_once": False,
        "wsgi.url_scheme": headers.get("X-Forwarded-Proto", "https"),
        "wsgi.version": (1, 0),
        "serverless.authorizer": event.get("requestContext", {}).get("authorizer"),
        "serverless.event": event,
        "serverless.context": context,
    })

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    django_app = get_wsgi_application()

    response = Response.from_app(django_app, environment)
    return generate_response(response, event)

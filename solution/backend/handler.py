#!/usr/bin/env python

"""
This module converts an AWS API Gateway proxied request to a WSGI request.

This is a simplified version of Logan Raarup's implementation from here:
https://github.com/logandk/serverless-wsgi/blob/master/serverless_wsgi.py

The main difference is that this version has all non-Django functionality stripped out to make it easier to maintain.
"""

import base64
import io
import os
import sys
from urllib.parse import unquote, urlencode, urlparse

from django.core.wsgi import get_wsgi_application
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response

# List of MIME types that should not be base64 encoded.
# MIME types within `text/*` are included by default.
TEXT_MIME_TYPES = [
    "application/json",
    "application/javascript",
    "application/xml",
    "application/vnd.api+json",
    "image/svg+xml",
]


# Load Django as a WSGI application.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
application = get_wsgi_application()


# Determine if a "stage name" path should be prepended to all requests.
# This is necessary for API Gateway requests that are not on a custom domain.
def get_script_name(headers, request_context):
    stage = os.environ.get("STAGE_ENV") or request_context.get("stage")
    host = urlparse(f"//{headers.get('Host', '')}", scheme="https").hostname or ""
    if stage and host.endswith(".amazonaws.com"):
        return f"/{stage}"
    return ""


# Get the body of the request, base64 decoded if necessary.
def get_body_bytes(event, body):
    if event.get("isBase64Encoded", False):
        return base64.b64decode(body)
    elif isinstance(body, str):
        return body.encode("utf-8")
    return body


# Set up the WSGI environment dictionary.
def setup_environment(headers, environment):
    for key, value in environment.items():
        if isinstance(value, str):
            environment[key] = value.encode("utf-8").decode("latin1", "replace")
    for key, value in headers.items():
        key = "HTTP_" + key.replace("-", "_").upper()
        if key not in ("HTTP_CONTENT_TYPE", "HTTP_CONTENT_LENGTH"):
            environment[key] = value
    return environment


# Generate all possible case permutations of a string.
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


# If there are multiple occurances of the same header, create case-mutated variations
# to pass them through to API Gateway.
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


# If there are multiple occurances of the same header, group them together.
def group_headers(headers):
    new_headers = {}
    for key in headers.keys():
        new_headers[key] = headers.get_all(key)
    return new_headers


# Generate the Lambda response dictionary from the WSGI response.
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


# Encode the query string parameters.
def encode_query_string(event):
    params = event.get("multiValueQueryStringParameters") or event.get("queryStringParameters") or event.get("query") or ""
    return urlencode(params, doseq=True)


def handler(event, context):
    # Retrieve headers either from multiValueHeaders or headers, depending on the request format.
    if "multiValueHeaders" in event and event["multiValueHeaders"]:
        headers = Headers(event["multiValueHeaders"])
    else:
        headers = Headers(event["headers"])

    script_name = get_script_name(headers, event.get("requestContext", {}))
    path_info = event["path"]
    body = get_body_bytes(event, event.get("body") or "")

    # Set up the initial WSGI environment.
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

    # Forward the request to Django and generate a response.
    response = Response.from_app(application, environment)
    return generate_response(response, event)

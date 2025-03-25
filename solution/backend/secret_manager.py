import json
import os

import boto3
from botocore.exceptions import BotoCoreError

try:
    client = boto3.client("secretsmanager")
except BotoCoreError:
    client = None
secret_cache = {}


# Get a secret from AWS Secrets Manager
#
# secret_id: The AWS ID of the secret to retrieve
# Returns: The secret as a dictionary
# Raises: botocore.exceptions.ClientError if the secret cannot be retrieved
def get_secret(secret_id):
    if secret_id not in secret_cache:
        response = client.get_secret_value(SecretId=secret_id)
        secret_cache[secret_id] = json.loads(response["SecretString"])
    return secret_cache[secret_id]


# Get a field from an AWS secret or environment variable
#
# secret_name: The environment variable containing the ID of the secret to retrieve
# field_name: The name of the field to retrieve
# environment_fallback: The environment variable to use as a fallback, if desired (typical use case is local dev)
# default: The default value to return if the secret cannot be retrieved
# Returns: The field as a string, or the default value if the secret cannot be retrieved
def get_secret_field(secret_name, field_name, environment_fallback=None, default=None):
    try:
        secret_id = os.environ[secret_name]
        return get_secret(secret_id)[field_name]
    except Exception:
        return os.environ.get(environment_fallback, default) if environment_fallback else default


# Get the username from an AWS secret or environment variable
#
# secret_name: The environment variable containing the ID of the secret to retrieve
# environment_fallback: The environment variable to use as a fallback, if desired (typical use case is local dev)
# default: The default value to return if the secret cannot be retrieved, if desired
# Returns: The username as a string, or the default value if the secret cannot be retrieved
def get_username(secret_name, environment_fallback=None, default=None):
    return get_secret_field(secret_name, "username", environment_fallback, default)


# Get the password from an AWS secret or environment variable
#
# secret_name: The environment variable containing the ID of the secret to retrieve
# environment_fallback: The environment variable to use as a fallback, if desired (typical use case is local dev)
# default: The default value to return if the secret cannot be retrieved, if desired
# Returns: The password as a string, or the default value if the secret cannot be retrieved
def get_password(secret_name, environment_fallback=None, default=None):
    return get_secret_field(secret_name, "password", environment_fallback, default)

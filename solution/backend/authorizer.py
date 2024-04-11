import base64
import os


def handler(event, context):
    # if a basic auth header is set, use that to find the correct user/token
    authorizationHeader = None
    if 'Authorization' in event['headers']:
        authorizationHeader = event["headers"]["Authorization"]
    if 'authorization' in event['headers']:
        authorizationHeader = event["headers"]["authorization"]
    if not authorizationHeader:
        raise Exception("Unauthorized")

    b64_token = authorizationHeader.split(" ")[-1]
    username, password = base64.b64decode(b64_token).decode("utf-8").split(":")
    expected_username = os.environ.get("HTTP_AUTH_USER")
    expected_password = os.environ.get("HTTP_AUTH_PASSWORD")

    if not expected_username or not expected_password or username != expected_username or password != expected_password:
        raise Exception("Unauthorized")

    return {
        "principalId": username,
        "usageIdentifierKey": password,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "%s/*" % "/".join(event["methodArn"].split("/")[0:2]),
                },
            ],
        },
    }

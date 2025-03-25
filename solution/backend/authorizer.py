import base64

from secret_manager import get_password, get_username


def handler(event, context):
    authorizationHeader = None
    if 'Authorization' in event['headers']:
        authorizationHeader = event["headers"]["Authorization"]
    if 'authorization' in event['headers']:
        authorizationHeader = event["headers"]["authorization"]
    if not authorizationHeader:
        raise Exception("Unauthorized")

    b64_token = authorizationHeader.split(" ")[-1]
    username, password = base64.b64decode(b64_token).decode("utf-8").split(":")

    expected_username = get_username("HTTP_AUTH_SECRET", environment_fallback="HTTP_AUTH_USER")
    expected_password = get_password("HTTP_AUTH_SECRET", environment_fallback="HTTP_AUTH_PASSWORD")

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

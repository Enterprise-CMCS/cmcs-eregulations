import os
from urllib.parse import urljoin


def handler(event, context):
    original_path = event['path']

    # Not using "get" because we want to fail if the environment variable is not set
    new_domain = os.environ["CUSTOM_URL"]

    response = {
        'statusCode': 302,
        'headers': {
            'Location': urljoin(new_domain, original_path),
        },
    }

    return response

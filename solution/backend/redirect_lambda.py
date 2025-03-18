import os
from urllib.parse import urljoin


def handler(event, context):
    original_path = event['path']

    # Not using "get" because we want to fail if the environment variable is not set
    new_domain = os.environ["CUSTOM_URL"]
    redirect_url = urljoin(f"https://{new_domain}", original_path)

    response = {
        'statusCode': 302,
        'headers': {
            'Location': redirect_url,
        },
    }

    return response

import os


def handler(event, context):
    # Not using "get" because we want to fail if the environment variable is not set
    new_domain = os.environ["CUSTOM_URL"]
    redirect_url = f"https://{new_domain}"

    response = {
        'statusCode': 302,
        'headers': {
            'Location': redirect_url,
        },
    }

    return response

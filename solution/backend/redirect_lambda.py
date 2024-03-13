from urllib.parse import urljoin


def handler(event, context):
    original_path = event['path']
    new_domain = 'https://eregulations.cms.gov'
    new_url = urljoin(new_domain, original_path)

    response = {
        'statusCode': 302,
        'headers': {
            'Location': new_url,
        },
    }

    return response

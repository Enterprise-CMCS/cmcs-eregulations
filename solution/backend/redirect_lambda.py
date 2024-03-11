import json

def lambda_handler(event, context):
    original_path = event['path']
    new_domain = 'https://eregulations.cms.gov'
    new_url = f'{new_domain}{original_path}'

    response = {
        'statusCode': 302,  # HTTP status code for redirection
        'headers': {
            'Location': new_url,  # Set the new URL in the Location header
        },
        'body': '',  # Empty body for a redirect response
    }

    return response

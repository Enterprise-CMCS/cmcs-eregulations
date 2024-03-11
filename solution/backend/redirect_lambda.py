def lambda_handler(event, context):
    original_path = event['path']
    new_domain = 'https://eregulations.cms.gov'
    new_url = f'{new_domain}{original_path}'

    response = {
        'statusCode': 302,
        'headers': {
            'Location': new_url,
        },
        'body': f'Redirecting to: {new_url}',

    }

    return response

from urllib.parse import urljoin


def handler(event, context):
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': "<html><body><h1>Hello world from CDK!</h1></body></html>",
    }

    return response

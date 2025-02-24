# maintenance/lambda_function.py

def handler(event, context):
    # HTML content for the maintenance page
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Maintenance</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background-color: #f4f4f4;
            }
            h1 {
                color: #333;
            }
            p {
                color: #666;
            }
            a {
                color: #0073e6;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Policy Connector is temporarily offline for maintenance.</h1>
    </body>
    </html>
    '''

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html'
        },
        'body': html_content
    }

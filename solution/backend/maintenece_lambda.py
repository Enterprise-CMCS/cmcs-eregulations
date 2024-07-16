# maintenance/lambda_function.py
import json

def lambda_handler(event, context):
    # HTML content for the maintenance page
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Maintenance</title>
    </head>
    <body>
        <h1>eRegulations is temporarily offline for maintenance.</h1>
        <p>You can use eCFR for regulations in the meantime. If you have any questions, please check the eRegs user help channel in CMS Slack (#cms-eregulations-help) or reach out to 
        <a href="mailto:britta.gustafson@a1msolutions.com">britta.gustafson@a1msolutions.com</a> and 
        <a href="mailto:stephanie.boyd@cms.hhs.gov">stephanie.boyd@cms.hhs.gov</a>.</p>
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

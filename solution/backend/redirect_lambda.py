def handler(event, context):
    redirect_url = "https://eregulations.cms.gov"
    response = {
        "statusCode": 302,
        "headers": {
            "Location": redirect_url,
        },
    }
    return response

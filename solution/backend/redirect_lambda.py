def handler(event, context):
    # URL to which you want to redirect
    redirect_url = "https://eregulations.cms.gov"
    response = {
        "statusCode": 302,
        "headers": {
            "Location": redirect_url,
        },
    }
    return response

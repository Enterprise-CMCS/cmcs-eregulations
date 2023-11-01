import json


def get_paginated_data(response):
    return json.loads(json.dumps(response.data))

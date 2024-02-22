import json
import re


def get_paginated_data(response):
    return json.loads(json.dumps(response.data))

def is_escaped(string):
    return bool(re.search(r'&\w+;', string))

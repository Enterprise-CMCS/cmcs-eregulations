import json
import re


def get_paginated_data(response):
    return json.loads(json.dumps(response.data))

def is_escaped(string):
    commonly_escaped = ['<', '>', '"', "'"]
    clean = True
    for i in commonly_escaped:
        if i in string:
            clean = False
            break

    return bool(re.search(r'&\w+;', string)) and clean

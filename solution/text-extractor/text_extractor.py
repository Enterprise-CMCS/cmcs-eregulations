import sys
import json

def handler(event, context):
    if event["rawPath"] == "/a":
        return None
    if event["rawPath"] == "/b":
        return 123
    if event["rawPath"] == "/c":
        return {
            "statusCode": 200,
            'headers': {'Content-Type': 'application/json'},
            "body": json.dumps({"message": "This is a test using Python " + sys.version + " in a Docker container"}),
        }
    if event["rawPath"] == "/d":
        return {}
    if event["rawPath"] == "/e":
        return
    if event["rawPath"] == "/f":
        return {
            "statusCode": 404,
        }

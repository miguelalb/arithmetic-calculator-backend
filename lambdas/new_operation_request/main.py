import json


def handler(event, context):
    body = {
        "message": "Create Operation Request Lambda",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}

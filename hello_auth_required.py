import json


def hello(event, context):
    body = {
        "message": "Authorization Granted: This function requires authorization!",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}

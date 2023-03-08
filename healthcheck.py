import json
from http import HTTPStatus


def hello(event, context):
    body = {
        "message": "Arithmetic Calculator REST API. Your function executed successfully!",
        "status": "Healthy!",
    }

    return {"statusCode": HTTPStatus.OK, "body": json.dumps(body)}

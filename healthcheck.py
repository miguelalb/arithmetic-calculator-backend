import json
from http import HTTPStatus


def hello(event, context):
    body = {
        "message": "Arithmetic Calculator REST API. Your function executed successfully!",
        "status": "Healthy!",
    }
    headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        }

    return {"headers": headers,"statusCode": HTTPStatus.OK, "body": json.dumps(body)}

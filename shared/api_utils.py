from typing import Union
from http import HTTPStatus

from shared.json_utils import dict_to_json_str


"""
Helper functions/classes for the API response handling
"""


class HTTPResponse:
    """
    Serialize to a valid AWS API Gateway REST API response object
    """
    def __init__(self,
                 status_code: HTTPStatus,
                 body: Union[dict, list, str]
                 ) -> None:
        self.status_code = int(status_code)
        self.body = dict_to_json_str(body)

    def to_dict(self) -> dict:
        return {
            'statusCode': self.status_code,
            'body': self.body
        }

import functools
from typing import Any, Callable, Union
from http import HTTPStatus

from shared.api_utils import HTTPResponse

"""
Helper functions/classes for errors and exception handling
"""


class HTTPException(Exception):
    """
    Base exception to raise HTTP 4xx, 5xx errors
    """
    def __init__(self,
                 status_code: Union[HTTPStatus, int],
                 msg: Any) -> None:
        self.status_code = status_code
        self.msg = msg
        super().__init__(str(self.msg))


def exception_handler(func: Callable) -> Callable:
    """
    Decorator to serialize responses, errors and exceptions to
    an HTTPResponse object that AWS API Gateway can understand.
    :param func: function to decorate
    :return: function wrapper
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            value: HTTPResponse = func(*args, **kwargs)
            return value.to_dict()
        except HTTPException as e:
            return HTTPResponse(status_code=e.status_code,
                                body=e.msg).to_dict()

    return wrapper

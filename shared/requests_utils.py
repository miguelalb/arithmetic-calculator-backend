"""
Common helper/utility functions used for making HTTP Requests
"""
import math
from http import HTTPStatus
from logging import Logger
from time import sleep

import requests


def request_with_retry(logger: Logger,
                       url: str,
                       request_method: str = 'GET',
                       headers: dict = {},
                       query_params: dict = {},
                       max_retries: int = 3,
                       sleep_time_milliseconds: int = 200,
                       ) -> dict:
    """
    Makes a request to an API endpoint and retries with exponential backoff if
    the request is not successful. If the request is successful, it returns the results.

    An exponential backoff algorithm retries requests exponentially, increasing the waiting
    time between retries up to a maximum backoff time or to a maximum number of retries (in
    this case just 3 times by default).

    This function is generic and can be used to call different APIs.
    To avoid overwhelming the API server, a short wait time is added between each request.
    Parameters:
        - logger (Logger): logger
        - url (str): The URL of the API endpoint to be called
        - request_method (str): The HTTP method to use (GET or POST) only for now
        - headers (dict): The HTTP Headers to send with the request
        - query_params (dict): The Query Parameters to send
        - max_retries (int): The maximum number of times to retry a failed request before giving up
        - sleep_time_milliseconds (int): The amount of milliseconds to wait before next request if succeeded
                                        this is to avoid overwhelming the server if the request is in a loop.
    Returns:
        Response json object (dict)
    """
    logger.info(f"Sending {request_method} request to URL {url}")
    sleep_time = sleep_time_milliseconds / 1000  # sleep before next api call, defaults to 200 milliseconds
    request_payload = {
        'url': url
    }

    request_method_map = {
        'GET': requests.get,
        'POST': requests.post,
        'PUT': requests.put,
        'PATCH': requests.patch,
        'DELETE': requests.delete
    }
    request_func = request_method_map[request_method]
    if headers:
        request_payload['headers'] = headers
    if query_params:
        request_payload['query_params'] = query_params

    request_succeeded: bool = lambda x: x < HTTPStatus.BAD_REQUEST

    r = request_func(url=url, params=query_params)
    if request_succeeded(r.status_code):
        sleep(sleep_time)
        return r.json()

    while max_retries > 0:
        logger.info("Retrying API Call")
        sleep(sleep_time)
        r = request_func(url=url, params=query_params)
        max_retries = max_retries - 1
        sleep_time = math.pow(sleep_time, 2)  # Exponential Backoff
        if request_succeeded(r.status_code):
            max_retries = 0
            sleep(sleep_time)
            return r.json()

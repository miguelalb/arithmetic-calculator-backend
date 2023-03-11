import logging
import os

import boto3
from pythonjsonlogger import jsonlogger

from lambdas.list_operations.processor import ListOperationsProcessor
from shared.api_utils import HTTPResponse
from shared.bootstrap import create_operations_if_not_exists
from shared.crud_service import CrudService
from shared.error_handling import exception_handler

# environment variables
LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'arithmetic-calculator-api-dev-ArithmeticCalculatorTable')

# logging
logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(LOGGING_LEVEL)

# AWS resources
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

crud_service = CrudService(logger=logger,
                           table=table)

create_operations_if_not_exists(logger=logger,
                                crud_service=crud_service)


@exception_handler
def handler(event: dict, context: dict) -> HTTPResponse:
    """
    List all Operations available.
    Includes pagination (page and per_page parameters), which is enabled by default with a
    10 per_page limit.

    You can also filter by operation type by providing the operation_type query parameters.
    """
    processor = ListOperationsProcessor(logger=logger,
                                        crud_service=crud_service)

    return processor.process_list_operations_event(event=event)

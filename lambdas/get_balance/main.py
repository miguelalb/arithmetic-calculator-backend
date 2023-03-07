import logging
import os

import boto3
from pythonjsonlogger import jsonlogger

from lambdas.get_balance.processor import GetBalanceEventProcessor
from shared.api_utils import HTTPResponse
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


@exception_handler
def handler(event: dict, context: dict) -> HTTPResponse:
    """
    Get the user's current balance.
    """
    processor = GetBalanceEventProcessor(logger=logger,
                                         crud_service=crud_service)

    return processor.process_get_balance_event(event=event)

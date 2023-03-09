import logging
import os

import boto3
from pythonjsonlogger import jsonlogger

from lambdas.list_records.processor import ListRecordsProcessor
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
    List all records for the current user.
    Includes pagination (page and per_page parameters), which is enabled by default with a
    10 per_page limit.

    You can also filter by record date or by user balance by providing the query parameters:
    - date_start
    - date_end
    - balance_start
    - balance_end

    If you provide a date_start value it returns user Records after that date (inclusive), if you
    also provide a date_end value it returns Records between the start and end dates (inclusive).
    However, if you only provide a value for the date_end, it returns Records before or equal
    to the provided end date.

    Similarly, if you provide a balance_start value it returns user Records greater than the
    balance provided (inclusive), if you also provide a balance_end value it returns Records
    between the balance_start and balance_end values (inclusive).
    However, if you only provide a value for the balance_end parameter, it returns Records less
    than or equal to the end balance provided.

    These filters are mutually exclusive, meaning you can either filter by date or filter by
    user balance. If you provide a date_start/date_end and also a balance_start/balance_end,
    it returns the Records that comply with the date filters.
    """
    processor = ListRecordsProcessor(logger=logger,
                                     crud_service=crud_service)

    return processor.process_list_records_event(event=event)

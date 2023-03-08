import logging
import os

import boto3
from pythonjsonlogger import jsonlogger

from lambdas.arithmetic_operation_worker.processor import ArithmeticOperationWorkerProcessor
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
def handler(event: dict, context: dict) -> None:
    """
    Arithmetic Operation Worker Lambda.
    This lambda is triggered by messages in the Arithmetic Operation SQS Queue and
    is responsible for performing all arithmetic operations (addition, subtraction,
    multiplication, division, and square_root).

    If the user has a record history but does not have sufficient funds, it drops the
    message and gets ready to process others.

    Otherwise, if the user does NOT have a record history (first operation) or the
    user has sufficient balance to cover for the operation cost, it performs the
    operation, deducts the operation cost from the balance, and saves a new
    Record with the results into the DynamoDB table.
    """
    processor = ArithmeticOperationWorkerProcessor(logger=logger,
                                                   crud_service=crud_service)

    for item in event.get('Records', []):
        processor.process_arithmetic_operation_event(event=item)

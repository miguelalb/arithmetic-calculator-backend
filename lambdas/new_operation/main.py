import logging
import os

import boto3
from pythonjsonlogger import jsonlogger

from lambdas.new_operation.processor import NewOperationEventProcessor
from shared.api_utils import HTTPResponse
from shared.bootstrap import create_operations_if_not_exists
from shared.crud_service import CrudService
from shared.error_handling import exception_handler
from shared.sns_service import SnsService

# environment variables
LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO')
ARITHMETIC_OPERATIONS_TOPIC_NAME = os.environ.get('ARITHMETIC_OPERATIONS_TOPIC_NAME', '')
GENERATE_RANDOM_STRING_TOPIC_NAME = os.environ.get('GENERATE_RANDOM_STRING_TOPIC_NAME', '')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'arithmetic-calculator-api-dev-ArithmeticCalculatorTable')

# logging
logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(LOGGING_LEVEL)

# AWS resources
sns_client = boto3.client('sns')
sns_service = SnsService(logger=logger,
                         sns_client=sns_client)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

crud_service = CrudService(logger=logger,
                           table=table)

create_operations_if_not_exists(logger=logger,
                                crud_service=crud_service)

@exception_handler
def handler(event: dict, context: dict) -> HTTPResponse:
    """
    Receives a new operation request and checks if the user has enough balance to
    cover the operation cost.

    If the user has a record history but does not have sufficient funds, it returns a
    400 bad request with an 'Insufficient funds to perform this operation' error msg
    and does not trigger any additional workflows.

    Otherwise, if the user does NOT have a record history (first operation) or the
    user has sufficient balance to cover for the operation cost it creates an
    OperationEventMessage which contains a unique `record_id`. It then proceeds to
    publish that message to either the 'arithmetic-operation' or 'generate-random-string'
    topic for downstream processing by the workers depending on the operation type.

    The message_id and unique record_id are then returned to the client so that it can
    poll for results.
    """
    processor = NewOperationEventProcessor(logger=logger,
                                           sns_service=sns_service,
                                           crud_service=crud_service,
                                           arithmetic_topic_name=ARITHMETIC_OPERATIONS_TOPIC_NAME,
                                           random_string_topic_name=GENERATE_RANDOM_STRING_TOPIC_NAME)

    return processor.process_new_operation_event(event=event)

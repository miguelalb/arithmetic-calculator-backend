import logging
import os

import boto3
from cachetools import FIFOCache
from pythonjsonlogger import jsonlogger

from lambdas.generate_random_string_worker.processor import GenerateRandomStringWorkerProcessor
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

# Random.org resources
max_cache_size = 10
random_string_cache = FIFOCache(maxsize=max_cache_size)
random_org_api_url = 'https://www.random.org/strings'
random_org_api_query_params = {
    'num': max_cache_size,
    'len': 8,
    'digits': 'on',
    'upperalpha': 'on',
    'loweralpha': 'on',
    'unique': 'on',
    'format': 'plain',
    'rnd': 'new'
}


@exception_handler
def handler(event: dict, context: dict) -> None:
    """
    Generate Random String Worker Lambda.
    This lambda is triggered by messages in the 'Generate Random String SQS Queue' and
    is responsible for performing requests to the Random.org api that generates a random
    string for the user.

    These requests are 'cached' in memory (there's a caveat to this, because AWS Lambda
    will generally terminate functions after 45–60 mins of inactivity, although idle
    functions can sometimes be terminated a lot earlier to free up resources needed by
    other customers) but this is a good addition to reduce the amount of calls to the
    random string generation API.

    In the rare case we ran out of quota (Random.org grants each IP address has a base
    quota of 1,000,000 bits) it defaults to generating a random string locally so that
    the user experience is seamless.

    If the user has a record history but does not have sufficient funds, it drops the
    message and gets ready to process others.

    Otherwise, if the user does NOT have a record history (first operation) or the
    user has sufficient balance to cover for the operation cost, it performs the
    operation, deducts the operation cost from the balance, and saves a new
    Record with the results into the DynamoDB table.
    """
    processor = GenerateRandomStringWorkerProcessor(logger=logger,
                                                    crud_service=crud_service,
                                                    random_org_api_url=random_org_api_url,
                                                    query_params=random_org_api_query_params,
                                                    random_string_cache=random_string_cache)

    for item in event.get('Records', []):
        processor.process_generate_random_string_event(event=item)

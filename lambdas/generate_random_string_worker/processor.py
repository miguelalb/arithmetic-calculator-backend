import string
import random
from logging import Logger

from cachetools import FIFOCache

from shared.date_utils import get_js_utc_now
from shared.crud_service import CrudService
from shared.json_utils import json_string_to_dict
from shared.models.operation_model import Operation, OperationType
from shared.models.record_model import RecordOUT, RecordIN, DEFAULT_INITIAL_USER_BALANCE
from shared.record_utils import get_user_most_recent_record, is_user_first_operation, check_user_has_sufficient_balance
from shared.requests_utils import request_with_retry

SINGLE_NUMBER_OPERATIONS = [OperationType.SQUARE_ROOT]


class GenerateRandomStringWorkerProcessor:
    def __init__(self,
                 logger: Logger,
                 crud_service: CrudService,
                 random_org_api_url: str,
                 query_params: dict,
                 random_string_cache: FIFOCache
                 ) -> None:
        self.logger = logger
        self.crud_service = crud_service
        self.random_org_api_url = random_org_api_url
        self.query_params = query_params
        self.random_string_cache = random_string_cache

    def process_generate_random_string_event(self, event: dict) -> None:
        body = json_string_to_dict(event.get('body', '{}'))
        record_id = body.get('record_id')
        user_id = body.get('user_id')
        operation_in = body.get('operation', {})
        operation = Operation(**operation_in)

        self.logger.info(f"Processing Generate Random String event for User {user_id}",
                         extra={'RecordId': record_id, 'Operation': operation.dict()})
        user_records_db = get_user_most_recent_record(crud_service=self.crud_service,
                                                      user_id=user_id)

        if is_user_first_operation(logger=self.logger,
                                   user_records_db=user_records_db):
            self.logger.info("User's first operation. Granting credit and calculating operation.")
            results = self._generate_random_string()

            self.logger.info("Deducting operation costs from initial balance")
            user_balance = DEFAULT_INITIAL_USER_BALANCE - operation.cost
            record_in = RecordIN(record_id=record_id,
                                 operation_id=operation.operation_id,
                                 user_id=user_id,
                                 amount=operation.cost,
                                 user_balance=user_balance,
                                 operation_response=results,
                                 date=get_js_utc_now())
            self.logger.info("Saving record to DB",
                             extra={'RecordIN': record_in.dict()})
            self.crud_service.create(item=record_in.dict())
            return

        user_record = RecordOUT(**user_records_db[0])
        check_user_has_sufficient_balance(logger=self.logger,
                                          operation=operation,
                                          recent_record=user_record)
        results = self._generate_random_string()
        self.logger.info("Deducting operation cost from current balance")
        user_balance = user_record.user_balance - operation.cost
        record_in = RecordIN(record_id=record_id,
                             operation_id=operation.operation_id,
                             user_id=user_id,
                             amount=operation.cost,
                             user_balance=user_balance,
                             operation_response=results,
                             date=get_js_utc_now())
        self.logger.info("Saving record to DB",
                         extra={'RecordIN': record_in.dict()})
        self.crud_service.create(item=record_in.dict())
        return

    def _generate_random_string(self) -> str:
        try:
            self.logger.info("Getting random string from Cache")
            random_string = self.random_string_cache.popitem()[0]
            self.logger.info("Returning random string",
                             extra={'RandomString': random_string})
            return random_string

        except KeyError:
            self.logger.info("Cache is empty. Calling random.org API.")
            response = request_with_retry(logger=self.logger,
                                          url=self.random_org_api_url,
                                          request_method='GET',
                                          query_params=self.query_params)
            if not response.text:
                self.logger.error("Unfortunately, we ran out of Random.org API Quota.")
                local_strings_list = self._generate_random_strings_locally(count=10,
                                                                           length=8)
                self.logger.info("Saving local random strings to cache",
                                 extra={'LocalStrings': local_strings_list})
                for local_string in local_strings_list:
                    self.random_string_cache[local_string] = local_string

                random_string = self.random_string_cache.popitem()[0]
                self.logger.info("Returning random string",
                                 extra={'RandomString': random_string})
                return random_string

            random_org_strings = response.text.strip().split('\n')
            self.logger.info("Saving Random.org strings to cache",
                             extra={'RandomOrgStrings': random_org_strings})
            for item in random_org_strings:
                self.random_string_cache[item] = item

            random_string = self.random_string_cache.popitem()[0]
            self.logger.info("Returning random string",
                             extra={'RandomString': random_string})
            return random_string

    def _generate_random_strings_locally(self, count: int, length: int) -> list:
        self.logger.info("Generating Random String Locally",
                         extra={'Count': count, 'StringsLength': length})
        string_list = []
        for _ in range(count):
            # choose from all lowercase letter
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(length))
            string_list.append(result_str)

        return string_list

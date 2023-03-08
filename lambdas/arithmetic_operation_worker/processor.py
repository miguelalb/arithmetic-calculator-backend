from logging import Logger
from typing import Union

from shared.date_utils import get_js_utc_now
from shared.arithmetic_utils import OPERATION_MAP
from shared.crud_service import CrudService
from shared.json_utils import json_string_to_dict
from shared.models.operation_model import Operation, OperationType
from shared.models.record_model import RecordOUT, RecordIN, DEFAULT_INITIAL_USER_BALANCE
from shared.record_utils import get_user_most_recent_record, is_user_first_operation, check_user_has_sufficient_balance

SINGLE_NUMBER_OPERATIONS = [OperationType.SQUARE_ROOT]


class ArithmeticOperationWorkerProcessor:
    def __init__(self,
                 logger: Logger,
                 crud_service: CrudService
                 ) -> None:
        self.logger = logger
        self.crud_service = crud_service

    def process_arithmetic_operation_event(self, event: dict) -> None:
        body = json_string_to_dict(event.get('body', '{}'))
        record_id = body.get('record_id')
        user_id = body.get('user_id')
        num1 = body.get('num1')
        num2 = body.get('num2')
        single_number = body.get('single_number')
        operation_in = body.get('operation', {})
        operation = Operation(**operation_in)

        self.logger.info(f"Processing Arithmetic Operation event for User {user_id}",
                         extra={'RecordId': record_id, 'Operation': operation.dict()})
        user_records_db = get_user_most_recent_record(crud_service=self.crud_service,
                                                      user_id=user_id)

        if is_user_first_operation(logger=self.logger,
                                   user_records_db=user_records_db):
            self.logger.info("User's first operation. Granting credit and calculating operation.")
            results = self._perform_arithmetic_operation(num1=num1,
                                                         num2=num2,
                                                         single_number=single_number,
                                                         operation=operation)

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
        results = self._perform_arithmetic_operation(num1=num1,
                                                     num2=num2,
                                                     single_number=single_number,
                                                     operation=operation)
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

    def _perform_arithmetic_operation(self,
                                      num1: Union[float, int],
                                      num2: Union[float, int],
                                      single_number: Union[float, int],
                                      operation: Operation
                                      ) -> Union[float, int]:
        """
        Maps the operation to perform based on operation type, performs the
        calculation and returns the result.
        :param num1: The first number
        :param num2: The second number
        :param single_number: For single number operations i.e. sqrt
        :param operation: The operation object
        :return: the operation result
        """
        self.logger.info("Doing calculation")
        operation_func = OPERATION_MAP[operation.type]

        if operation.type in SINGLE_NUMBER_OPERATIONS:
            return operation_func(single_number)

        return operation_func(num1, num2)

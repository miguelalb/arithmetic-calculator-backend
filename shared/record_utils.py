"""
Common helper/utility functions used for Record entity
"""
from http import HTTPStatus
from logging import Logger
from typing import Union

from shared.crud_service import ConditionType, CrudService
from shared.date_utils import get_js_utc_now
from shared.error_handling import HTTPException
from shared.models.operation_model import OperationOUT, Operation
from shared.models.record_model import RecordOUT


def is_user_first_operation(logger: Logger, user_records_db: list) -> bool:
    """
    Each user has an initial credit/balance. If this user doesn't have an operation
    history it means this is their first time they're doing an operation.

    The initial balance will be granted (and operation costs deducted from it) in
    the downstream worker lambda that processes the operation event message.
    :param logger: logger
    :param user_records_db: User Recent Records
    :return: True if this is the first user operation, otherwise False
    """
    logger.info("Checking if this is the user's first operation.")
    return not user_records_db


def check_user_has_sufficient_balance(logger: Logger,
                                      operation: Union[OperationOUT, Operation],
                                      recent_record: RecordOUT
                                      ) -> None:
    """
    Checks if the user has sufficient balance to cover for the operation cost
    :param logger: logger
    :param operation: The operation the user wants to perform
    :param recent_record: The most recent user Record.
    :return: None
    """
    logger.info("Checking that the user has sufficient balance.")
    if recent_record.user_balance < operation.cost:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            msg='Insufficient Funds to perform this operation')


def get_user_most_recent_record(crud_service: CrudService, user_id: str) -> list:
    """
    Gets the user's most recent Record.
    :param crud_service: Crud Service
    :param user_id: ID of the user
    :return: Record DB object
    """
    return crud_service.list_items(pk=f'User#{user_id}',
                                   gsi1=True,
                                   ascending=False,
                                   limit=1,
                                   condition_type=ConditionType.LESS_THAN_OR_EQUAL,
                                   condition_value=f'Record#{get_js_utc_now()}')

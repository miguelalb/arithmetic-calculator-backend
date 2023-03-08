from http import HTTPStatus
from typing import Union, Optional
from uuid import uuid4

from shared.models.base import Base
from shared.error_handling import HTTPException

from shared.models.operation_model import Operation, OperationType


class OperationEventMessage(Base):
    """
    SNS Message schema for operation events.
    """
    user_id: str
    record_id: str
    num1: Optional[Union[float, int]] = None
    num2: Optional[Union[float, int]] = None
    single_number: Optional[Union[float, int]] = None
    operation: Operation

    def __init__(self, **data):
        mapped_fields = map_to_sns_topic_format(data)
        super(OperationEventMessage, self).__init__(**mapped_fields)


def map_to_sns_topic_format(data) -> dict:
    data['record_id'] = data.get('record_id', str(uuid4()))
    validate_data(data)
    return data


def validate_data(data) -> None:
    """
    Operation input data validation
    :param data: input data
    """
    operation = data['operation']
    operation_type = operation['type'] if isinstance(operation, dict) else operation.type

    if operation_type == OperationType.RANDOM_STRING:
        pass

    elif operation_type == OperationType.SQUARE_ROOT:
        validate_square_root_input_data(data)
    else:
        validate_arithmetic_operation_data(data, operation_type)


def validate_square_root_input_data(data):
    single_number = data.get('single_number')
    if not single_number:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            msg='Invalid operation: Provide a number for the sqrt.')
    if single_number < 0:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            msg='Invalid operation: Cannot get square root of negative number.')


def validate_arithmetic_operation_data(data, operation_type):
    if data.get('num1') and not data.get('num2'):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            msg='Invalid Operation: needs a second value for operation to be complete')
    if data.get('num2') and not data.get('num1'):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            msg='Invalid operation: needs a first value for operation to be complete')
    if operation_type == OperationType.DIVISION and data.get('num2') == 0:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            msg='Invalid operation: Cannot divide a number by Zero')



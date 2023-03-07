from http import HTTPStatus
from typing import Union, Optional
from uuid import uuid4

from shared.models.base import Base
from shared.error_handling import HTTPException

from shared.models.operation_model import Operation


class OperationEventMessage(Base):
    """
    SNS Message schema for operation events.
    """
    user_id: str
    record_id: str
    num1: Optional[Union[float, int]] = None
    num2: Optional[Union[float, int]] = None
    operation: Operation

    def __init__(self, **data):
        mapped_fields = map_to_sns_topic_format(data)
        super(OperationEventMessage, self).__init__(**mapped_fields)


def map_to_sns_topic_format(data) -> dict:
    data['record_id'] = data.get('record_id', str(uuid4()))
    validate_data(data)
    return data


def validate_data(data):
    if data.get('num1') and not data.get('num2'):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            msg='needs a second value for operation to be complete')

    if data.get('num2') and not data.get('num1'):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            msg='needs a first value for operation to be complete')

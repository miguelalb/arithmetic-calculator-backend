from enum import Enum
from typing import Union, Optional
from uuid import uuid4

from pydantic import BaseModel

from models.operation_model import Operation


class RequestType(str, Enum):
    ARITHMETIC_OPERATION = 'ARITHMETIC_OPERATION'
    RANDOM_STRING_OPERATION = 'RANDOM_STRING_OPERATION'


class OperationRequest(BaseModel):
    user_id: str
    record_id: str
    request_type: RequestType
    num1: Optional[Union[float, int]] = None
    num2: Optional[Union[float, int]] = None
    operation: Operation

    def __init__(self, **data):
        mapped_fields = map_to_sns_topic_format(data)
        super(OperationRequest, self).__init__(**mapped_fields)


def map_to_sns_topic_format(data) -> dict:
    data['record_id'] = str(uuid4())
    if data.get('num1') and not data.get('num2'):
        raise ValueError('needs a second value for operation to be complete')

    if data.get('num2') and not data.get('num1'):
        raise ValueError('needs a first value for operation to be complete')

    return data

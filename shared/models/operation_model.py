from enum import Enum
from uuid import uuid4

from shared.models.base import Base


class OperationType(str, Enum):
    ADDITION = 'ADDITION'
    SUBTRACTION = 'SUBTRACTION'
    MULTIPLICATION = 'MULTIPLICATION'
    DIVISION = 'DIVISION'
    SQUARE_ROOT = 'SQUARE_ROOT'
    RANDOM_STRING = 'RANDOM_STRING'


class OperationBase(Base):
    """
    The Operation that the user wants to perform.
    """
    entity: str = "OPERATION"
    type: OperationType
    cost: int = 1


class Operation(OperationBase):
    """
    Represents an Operation model
    """
    operation_id: str


class OperationIN(OperationBase):
    """
    Represents an Operation create model object.
    """
    PK: str
    SK: str
    GSI1PK: str
    GSI1SK: str

    def __init__(self, **data):
        mapped_fields = map_to_dynamodb_format(data)
        super(OperationIN, self).__init__(**mapped_fields)


class OperationOUT(OperationBase):
    """
    Represents an Operation view object coming from DynamoDB.
    """
    operation_id: str

    def __init__(self, **data):
        mapped_fields = map_from_dynamodb_format(data)
        super(OperationOUT, self).__init__(**mapped_fields)


def map_to_dynamodb_format(data: dict) -> dict:
    """
    Add/Map the fields required to save object on DynamoDB.
    :param data:
    :return: mapped fields
    """
    operation_uuid = str(uuid4())
    operation_type = data['type']
    data['PK'] = 'Operation'
    data['SK'] = f'Operation#{operation_uuid}'
    data['GSI1PK'] = 'Operation'
    data['GSI1SK'] = f'Operation#{operation_type}'
    return data


def map_from_dynamodb_format(data: dict) -> dict:
    """
    Prepare the object for presentation by removing the DynamoDB
    internal implementation detail fields from the object.
    Parse Operation uuid from SK.
    :param data:
    :return: mapped fields
    """
    sk: str = data.pop('SK', '')
    data['operation_id'] = sk.split('#')[1]
    return data

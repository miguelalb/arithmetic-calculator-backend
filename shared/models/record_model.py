import os
from typing import Union

from shared.models.base import Base

from shared.date_utils import get_js_utc_now

DEFAULT_INITIAL_USER_BALANCE = int(os.environ.get('DEFAULT_INITIAL_USER_BALANCE', 30))


class RecordBase(Base):
    """
    The Record acts as a ledger that stores all the operations
    performed by the user, their cost and the user balance.

    Attribute definitions:
    - operation_id: ID of the operation
    - user_id: ID of the user
    - amount: Cost of the operation
    - user_balance: Resulting balance after cost was deducted
    - date: Date when the operation was performed (in epoch format)
    """
    entity: str = "RECORD"
    record_id: str  # Comes from the OperationRequest model
    operation_id: str
    user_id: str
    amount: int
    user_balance: int
    operation_response: Union[str, int, float]
    date: int  # epoch
    deleted: bool = False


class Record(RecordBase):
    """
    Represents a Record model
    """
    pass


class RecordIN(RecordBase):
    """
    Represents a Record create model object.
    """
    PK: str
    SK: str
    GSI1PK: str
    GSI1SK: str
    GSI2PK: str
    GSI2SK: str

    def __init__(self, **data):
        mapped_fields = map_to_dynamodb_format(data)
        super(RecordIN, self).__init__(**mapped_fields)


class RecordOUT(RecordBase):
    """
    Represents a Record view object coming from DynamoDB.
    """

    def __init__(self, **data):
        mapped_fields = map_from_dynamodb_format(data)
        super(RecordOUT, self).__init__(**mapped_fields)


def map_to_dynamodb_format(data: dict) -> dict:
    """
    Add/Map the fields required to save object on DynamoDB.
    :param data:
    :return: mapped fields
    """
    record_uuid = data.get('record_id', '')
    user_uuid = data.get('user_id', '')
    date = data.get('date', get_js_utc_now())
    user_balance = data.get('user_balance', DEFAULT_INITIAL_USER_BALANCE)

    user_balance = zero_negative_balance(user_balance)

    data['PK'] = f'User#{user_uuid}'
    data['SK'] = f'Record#{record_uuid}'
    data['GSI1PK'] = f'User#{user_uuid}'
    data['GSI1SK'] = f'Record#{date}'
    data['GSI2PK'] = f'User#{user_uuid}'
    data['GSI2SK'] = f'Record#{user_balance}'

    return data


def zero_negative_balance(user_balance):
    """
    Check if user balance is negative and set it to zero if it is.
    Negative balance is not allowed.

    *Note: This function may never be called because the workers check
    for sufficient balance before performing an operation, but
    is nice to have to avoid weird bugs.*

    :param user_balance: the user balance
    :return: zero
    """
    if user_balance < 0:
        user_balance = 0
    return user_balance


def map_from_dynamodb_format(data: dict) -> dict:
    """
    Prepare the object for presentation by removing the DynamoDB
    internal implementation detail fields from the object.
    Parse Record uuid from SK.
    :param data:
    :return: mapped fields
    """
    sk: str = data.pop('SK', '')
    data['record_id'] = sk.split('#')[1]
    return data

from uuid import uuid4

from pydantic import BaseModel

from shared.date_utils import get_js_utc_now


class RecordBase(BaseModel):
    """
    The Record acts as a ledger that stores all the operations performed by the user, their cost and the user balance
    Attribute definitions:
    - operation_id: ID of the operation
    - user_id: ID of the user
    - amount: Cost of the operation
    - user_balance: Resulting balance after cost was deducted
    - date: Date when the operation was performed (in epoch format)
    """
    entity: str = "RECORD"
    operation_id: str
    user_id: str
    amount: int
    user_balance: int
    operation_response: str
    date: int  # epoch


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
    Represents a Record view object.
    """
    record_id: str

    def __init__(self, **data):
        mapped_fields = map_from_dynamodb_format(data)
        super(RecordOUT, self).__init__(**mapped_fields)


def map_to_dynamodb_format(data: dict) -> dict:
    """
    Add/Map the fields required to save object on DynamoDB.
    :param data:
    :return: mapped fields
    """
    record_uuid = str(uuid4())
    user_uuid = data.get('user_id', '')
    date = get_js_utc_now()
    user_balance = data.get('user_balance', '')

    data['PK'] = f'User#{user_uuid}'
    data['SK'] = f'Record#{record_uuid}'
    data['GSI1PK'] = f'User#{user_uuid}'
    data['GSI1SK'] = f'Record{date}'
    data['GSI2PK'] = f'User#{user_uuid}'
    data['GSI2SK'] = f'Record#{user_balance}'

    return data


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

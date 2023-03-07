import pytest

from shared.fixture_utils import json_fixture
from shared.models.operation_request_msg_model import OperationEventMessage

OPERATION_REQUEST_VALID = json_fixture('operation_request_valid.json')
OPERATION_REQUEST_NUM2_MISSING = json_fixture('operation_request_num2_missing.json')
OPERATION_REQUEST_NUM1_MISSING = json_fixture('operation_request_num1_missing.json')


def test_operation_request_success():
    data = OPERATION_REQUEST_VALID
    operation_request = OperationEventMessage(**data)
    operation_request_dict = operation_request.dict()

    assert 'record_id' in operation_request_dict
    for k, v in data.items():
        assert operation_request_dict[k] == v


def test_num2_missing_raises_validation_error():
    data = OPERATION_REQUEST_NUM2_MISSING
    with pytest.raises(ValueError):
        OperationEventMessage(**data)


def test_num1_missing_raises_validation_error():
    data = OPERATION_REQUEST_NUM1_MISSING
    with pytest.raises(ValueError):
        OperationEventMessage(**data)

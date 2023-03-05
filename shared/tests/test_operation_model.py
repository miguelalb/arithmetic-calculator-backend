import pytest
from pydantic import ValidationError

from shared.fixture_utils import json_fixture
from shared.models.operation_model import OperationIN, OperationOUT

OPERATION_CREATE_DATA_VALID = json_fixture('operation_create_data_valid.json')
OPERATION_CREATE_DATA_INVALID = json_fixture('operation_create_data_invalid.json')


def test_operation_create_success():
    data = OPERATION_CREATE_DATA_VALID
    operation = OperationIN(**data)
    operation_dict = operation.dict()

    assert 'PK' in operation_dict.keys()
    assert 'SK' in operation_dict.keys()
    assert 'GSI1PK' in operation_dict.keys()
    assert 'GSI1SK' in operation_dict.keys()
    assert operation_dict['entity'] == 'OPERATION'
    for key, value in data.items():
        assert operation_dict[key] == value


def test_invalid_operation_input_raises_validation_error():
    data = OPERATION_CREATE_DATA_INVALID
    with pytest.raises(ValidationError):
        OperationIN(**data)


def test_operation_json_serialization():
    data = OPERATION_CREATE_DATA_VALID
    operation = OperationIN(**data)
    operation_out = OperationOUT(**operation.dict())
    operation_out_dict = operation_out.dict()

    assert 'operation_id' in operation_out_dict.keys()
    for key, value in data.items():
        assert operation_out_dict[key] == value

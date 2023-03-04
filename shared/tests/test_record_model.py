import pytest
from pydantic import ValidationError

from shared.fixture_utils import json_fixture
from shared.models.record_model import RecordIN, RecordOUT

RECORD_CREATE_DATA_VALID = json_fixture('record_create_data_valid.json')
RECORD_CREATE_DATA_INVALID = json_fixture('record_create_data_invalid.json')


def test_record_create_success():
    data = RECORD_CREATE_DATA_VALID
    record = RecordIN(**data)
    record_dict = record.dict()

    assert 'PK' in record_dict.keys()
    assert 'SK' in record_dict.keys()
    assert 'GSI1PK' in record_dict.keys()
    assert 'GSI1SK' in record_dict.keys()
    assert 'GSI2PK' in record_dict.keys()
    assert 'GSI2SK' in record_dict.keys()
    assert record_dict['entity'] == 'RECORD'
    for key, value in data.items():
        assert record_dict[key] == value


def test_invalid_record_input_raises_validation_error():
    data = RECORD_CREATE_DATA_INVALID
    with pytest.raises(ValidationError):
        RecordIN(**data)


def test_record_json_serialization():
    data = RECORD_CREATE_DATA_VALID
    record = RecordIN(**data)
    record_out = RecordOUT(**record.dict())
    record_out_dict = record_out.dict()

    assert 'record_id' in record_out_dict.keys()
    for key, value in data.items():
        assert record_out_dict[key] == value

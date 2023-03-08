from http import HTTPStatus

import pytest
from mock import MagicMock

from lambdas.delete_record.processor import DeleteRecordProcessor
from shared.error_handling import HTTPException
from shared.fixture_utils import json_fixture
from shared.json_utils import json_string_to_dict

mock_logger = MagicMock()
mock_crud_service = MagicMock()

DELETE_RECORD_EVENT_VALID = json_fixture('delete_record_event_valid.json')
DELETE_RECORD_UPDATE_RETURN_VALUE = json_fixture('delete_record_update_return_value.json')
DELETE_RECORD_EVENT_VALID_EXPECTED = json_fixture('delete_record_event_valid_expected.json')


def reset_mocks():
    mock_logger.reset_mock()
    mock_crud_service.reset_mock()


@pytest.fixture(scope="module")
def processor() -> DeleteRecordProcessor:
    reset_mocks()
    return DeleteRecordProcessor(logger=mock_logger,
                                 crud_service=mock_crud_service)


def test_delete_record_success(processor):
    event = DELETE_RECORD_EVENT_VALID
    mock_crud_service.update_item_attributes.return_value = DELETE_RECORD_UPDATE_RETURN_VALUE
    result = processor.process_delete_record_event(event=event)

    expected = DELETE_RECORD_EVENT_VALID_EXPECTED

    assert result.status_code == HTTPStatus.OK
    assert json_string_to_dict(result.body) == expected


def test_delete_record_no_record_raises_404(processor):
    event = DELETE_RECORD_EVENT_VALID
    mock_crud_service.update_item_attributes.return_value = None
    with pytest.raises(HTTPException):
        processor.process_delete_record_event(event=event)

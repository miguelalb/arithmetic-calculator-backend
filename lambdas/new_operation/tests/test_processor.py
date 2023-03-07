import pytest

from mock import MagicMock
from shared.fixture_utils import json_fixture
from lambdas.new_operation.processor import NewOperationEventProcessor

mock_logger = MagicMock()
mock_sns_service = MagicMock()
mock_crud_service = MagicMock()

NEW_OPERATION_EVENT_VALID = json_fixture('new_operation_event_valid.json')
LIST_ITEMS_GET_OPERATION_RETURN_VALUE = json_fixture('list_items_get_operation_return_value.json')
LIST_ITEMS_GET_USER_RECORDS_RETURN_VALUE = json_fixture('list_items_get_user_records_return_value.json')


@pytest.fixture()
def processor():
    return NewOperationEventProcessor(logger=mock_logger,
                                      sns_service=mock_sns_service,
                                      crud_service=mock_crud_service,
                                      arithmetic_topic_name='arithmetic-topic',
                                      random_string_topic_name='random-string-topic')


def test_new_operation_event_success(processor):
    data = NEW_OPERATION_EVENT_VALID
    mock_crud_service.list_items.side_effect = [
        LIST_ITEMS_GET_OPERATION_RETURN_VALUE,
        LIST_ITEMS_GET_USER_RECORDS_RETURN_VALUE
    ]
    mock_sns_service.publish_message.return_value = {'MessageId': ''}
    result = processor.process_new_operation_event(event=data)

    assert 'RecordId' in result.body
    assert 'MessageId' in result.body
    mock_sns_service.publish_message.assert_called()


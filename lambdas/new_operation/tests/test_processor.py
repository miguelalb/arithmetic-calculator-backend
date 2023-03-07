import pytest

from mock import MagicMock, patch
from shared.fixture_utils import json_fixture
from lambdas.new_operation.processor import NewOperationEventProcessor
from shared.models.operation_request_msg_model import OperationEventMessage

mock_logger = MagicMock()
mock_sns_service = MagicMock()
mock_crud_service = MagicMock()
mock_operation_event_message = MagicMock()

NEW_OPERATION_EVENT_VALID = json_fixture('new_operation_event_valid.json')
LIST_ITEMS_GET_OPERATION_RETURN_VALUE = json_fixture('list_items_get_operation_return_value.json')
LIST_ITEMS_GET_USER_RECORDS_RETURN_VALUE = json_fixture('list_items_get_user_records_return_value.json')
OPERATION_EVENT_MESSAGE_RETURN_VALUE = json_fixture('operation_event_message_return_value.json')


@pytest.fixture()
def processor():
    return NewOperationEventProcessor(logger=mock_logger,
                                      sns_service=mock_sns_service,
                                      crud_service=mock_crud_service,
                                      arithmetic_topic_name='arithmetic-topic',
                                      random_string_topic_name='random-string-topic')


@patch('lambdas.new_operation.processor.OperationEventMessage', mock_operation_event_message)
def test_new_operation_event_success(processor):
    data = NEW_OPERATION_EVENT_VALID
    mock_crud_service.list_items.side_effect = [
        LIST_ITEMS_GET_OPERATION_RETURN_VALUE,
        LIST_ITEMS_GET_USER_RECORDS_RETURN_VALUE
    ]
    operation_event_return = OperationEventMessage(**OPERATION_EVENT_MESSAGE_RETURN_VALUE)
    mock_operation_event_message.return_value = operation_event_return
    mock_sns_service.publish_message.return_value = {'MessageId': ''}
    result = processor.process_new_operation_event(event=data)

    assert 'RecordId' in result.body
    assert 'MessageId' in result.body
    mock_sns_service.publish_message.assert_called_with(topic_name='arithmetic-topic',
                                                        message=operation_event_return.to_string())


@patch('lambdas.new_operation.processor.OperationEventMessage', mock_operation_event_message)
def test_new_operation_event_random_string_success(processor):
    pass


@patch('lambdas.new_operation.processor.OperationEventMessage', mock_operation_event_message)
def test_new_operation_event_raises_exception_on_insufficient_funds(processor):
    pass

import pytest

from mock import MagicMock, patch
from shared.fixture_utils import json_fixture
from lambdas.new_operation.processor import NewOperationEventProcessor
from shared.models.operation_request_msg_model import OperationEventMessage
from shared.error_handling import HTTPException
from shared.json_utils import json_string_to_dict

mock_logger = MagicMock()
mock_sns_service = MagicMock()
mock_crud_service = MagicMock()
mock_operation_event_message = MagicMock()

NEW_OPERATION_EVENT_VALID = json_fixture('new_operation_event_valid.json')
NEW_OPERATION_RANDOM_STRING_EVENT_VALID = json_fixture('new_operation_random_string_valid.json')
LIST_ITEMS_GET_OPERATION_RETURN_VALUE = json_fixture('list_items_get_operation_return_value.json')
LIST_ITEMS_OPERATION_RANDOM_STRING_RETURN_VALUE = json_fixture('list_items_operation_random_string_return_value.json')
LIST_ITEMS_GET_USER_NO_RECORDS_RETURN_VALUE = json_fixture('list_items_get_user_no_records_return_value.json')
LIST_ITEMS_RECORD_INSUFFICIENT_FUNDS_RETURN_VALUE = json_fixture('list_items_record_insufficient_funds_return.json')
OPERATION_EVENT_MSG_RETURN_VALUE = json_fixture('operation_event_msg_return_value.json')
OPERATION_EVENT_MSG_RANDOM_STRING_RETURN_VALUE = json_fixture('operation_event_msg_random_string_return_value.json')


def reset_mocks():
    mock_logger.reset_mock()
    mock_sns_service.reset_mock()
    mock_crud_service.reset_mock()
    mock_operation_event_message.reset_mock()


@pytest.fixture()
def processor() -> NewOperationEventProcessor:
    reset_mocks()
    return NewOperationEventProcessor(logger=mock_logger,
                                      sns_service=mock_sns_service,
                                      crud_service=mock_crud_service,
                                      arithmetic_topic_name='arithmetic-topic',
                                      random_string_topic_name='random-string-topic')


@patch('lambdas.new_operation.processor.OperationEventMessage', mock_operation_event_message)
def test_new_operation_event_arithmetic_success(processor):
    event = NEW_OPERATION_EVENT_VALID
    mock_crud_service.list_items.side_effect = [
        LIST_ITEMS_GET_OPERATION_RETURN_VALUE,
        LIST_ITEMS_GET_USER_NO_RECORDS_RETURN_VALUE
    ]
    operation_event_return = OperationEventMessage(**OPERATION_EVENT_MSG_RETURN_VALUE)
    mock_operation_event_message.return_value = operation_event_return
    mock_sns_service.publish_message.return_value = 'f7121d00-c7c5-4290-8cc7-1ccc7460e3e8'
    result = processor.process_new_operation_event(event=event)

    assert json_string_to_dict(result.body) == {
        'MessageId': 'f7121d00-c7c5-4290-8cc7-1ccc7460e3e8',
        'RecordId': '1db72b27-7de6-4bc0-9c7c-44540e6311a5'
    }
    mock_sns_service.publish_message.assert_called_with(topic_name='arithmetic-topic',
                                                        message=operation_event_return.to_string())


@patch('lambdas.new_operation.processor.OperationEventMessage', mock_operation_event_message)
def test_new_operation_event_random_string_success(processor):
    event = NEW_OPERATION_RANDOM_STRING_EVENT_VALID
    mock_crud_service.list_items.side_effect = [
        LIST_ITEMS_OPERATION_RANDOM_STRING_RETURN_VALUE,
        LIST_ITEMS_GET_USER_NO_RECORDS_RETURN_VALUE
    ]
    operation_event_return = OperationEventMessage(**OPERATION_EVENT_MSG_RANDOM_STRING_RETURN_VALUE)
    mock_operation_event_message.return_value = operation_event_return
    mock_sns_service.publish_message.return_value = ''
    result = processor.process_new_operation_event(event=event)

    assert 'RecordId' in result.body
    assert 'MessageId' in result.body
    mock_sns_service.publish_message.assert_called_with(topic_name='random-string-topic',
                                                        message=operation_event_return.to_string())


@patch('lambdas.new_operation.processor.OperationEventMessage', mock_operation_event_message)
def test_new_operation_event_raises_exception_on_insufficient_funds(processor):
    event = NEW_OPERATION_RANDOM_STRING_EVENT_VALID
    mock_crud_service.list_items.side_effect = [
        LIST_ITEMS_OPERATION_RANDOM_STRING_RETURN_VALUE,
        LIST_ITEMS_RECORD_INSUFFICIENT_FUNDS_RETURN_VALUE
    ]
    operation_event_return = OperationEventMessage(**OPERATION_EVENT_MSG_RANDOM_STRING_RETURN_VALUE)
    mock_operation_event_message.return_value = operation_event_return
    mock_sns_service.publish_message.return_value = ''
    with pytest.raises(HTTPException):
        processor.process_new_operation_event(event=event)

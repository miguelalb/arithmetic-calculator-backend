import pytest
from mock import MagicMock

from lambdas.list_operations.processor import ListOperationsProcessor
from shared.crud_service import ConditionType
from shared.fixture_utils import json_fixture

mock_logger = MagicMock()
mock_crud_service = MagicMock()

LIST_OPERATIONS_EVENT_VALID = json_fixture('list_operations_event_valid.json')
LIST_ITEMS_OPERATIONS_RETURN_VALUE = json_fixture('list_items_operations_return_value.json')


@pytest.fixture(scope="module")
def processor() -> ListOperationsProcessor:
    return ListOperationsProcessor(logger=mock_logger,
                                   crud_service=mock_crud_service)


def test_list_operations_no_parameters(processor):
    event = LIST_OPERATIONS_EVENT_VALID
    mock_crud_service.list_items.return_value = LIST_ITEMS_OPERATIONS_RETURN_VALUE
    processor.process_list_operations_event(event=event)

    expected = {
        'pk': 'Operation',
        'condition_type': ConditionType.BEGINS_WITH,
        'condition_value': 'Operation#'
    }
    mock_crud_service.list_items.assert_called_with(**expected)


def test_list_operations_operation_type_parameter(processor):
    event = LIST_OPERATIONS_EVENT_VALID
    event['queryStringParameters'] = {'operation_type': 'addition'}
    mock_crud_service.list_items.return_value = LIST_ITEMS_OPERATIONS_RETURN_VALUE
    processor.process_list_operations_event(event=event)

    expected = {
        'pk': 'Operation',
        'gsi1': True,
        'condition_type': ConditionType.BEGINS_WITH,
        'condition_value': 'Operation#ADDITION'
    }
    mock_crud_service.list_items.assert_called_with(**expected)

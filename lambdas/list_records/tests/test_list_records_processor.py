from http import HTTPStatus

import pytest
from mock import MagicMock

from lambdas.list_records.processor import ListRecordsProcessor
from shared.crud_service import ConditionType
from shared.fixture_utils import json_fixture

mock_logger = MagicMock()
mock_crud_service = MagicMock()

LIST_RECORDS_EVENT_VALID = json_fixture('list_records_event_valid.json')
LIST_RECORDS_CRUD_RETURN_VALUE = json_fixture('list_records_crud_return_value.json')


@pytest.fixture(scope="module")
def processor() -> ListRecordsProcessor:
    return ListRecordsProcessor(logger=mock_logger,
                                crud_service=mock_crud_service)


def test_list_records_no_filter(processor):
    event = LIST_RECORDS_EVENT_VALID
    mock_crud_service.list_items.return_value = LIST_RECORDS_CRUD_RETURN_VALUE
    processor.process_list_records_event(event=event)

    expected = {
        'pk': f'User#77d46173-1d59-48d0-8b75-eaa76eb857b2',
        'gsi1': True,
        'gsi2': False,
        'condition_type': ConditionType.BEGINS_WITH,
        'condition_value': 'Record#'
    }
    mock_crud_service.list_items.assert_called_with(**expected)


def test_list_records_date_start_provided(processor):
    event = LIST_RECORDS_EVENT_VALID
    event['queryStringParameters'] = {'date_start': '1234'}
    mock_crud_service.list_items.return_value = LIST_RECORDS_CRUD_RETURN_VALUE
    processor.process_list_records_event(event=event)

    expected = {
        'pk': f'User#77d46173-1d59-48d0-8b75-eaa76eb857b2',
        'gsi1': True,
        'condition_type': ConditionType.GREATER_THAN_OR_EQUAL,
        'condition_value': f'Record#1234'
    }
    mock_crud_service.list_items.assert_called_with(**expected)


def test_list_records_date_start_and_date_end_provided(processor):
    event = LIST_RECORDS_EVENT_VALID
    event['queryStringParameters'] = {'date_start': '1234', 'date_end': '5678'}
    mock_crud_service.list_items.return_value = LIST_RECORDS_CRUD_RETURN_VALUE
    processor.process_list_records_event(event=event)

    expected = {
        'pk': f'User#77d46173-1d59-48d0-8b75-eaa76eb857b2',
        'gsi1': True,
        'condition_type': ConditionType.BETWEEN,
        'low_value': f'Record#1234',
        'high_value': f'Record#5678'
    }
    mock_crud_service.list_items.assert_called_with(**expected)


def test_list_records_date_end_only(processor):
    event = LIST_RECORDS_EVENT_VALID
    event['queryStringParameters'] = {'date_end': '5678'}
    mock_crud_service.list_items.return_value = LIST_RECORDS_CRUD_RETURN_VALUE
    processor.process_list_records_event(event=event)

    expected = {
        'pk': f'User#77d46173-1d59-48d0-8b75-eaa76eb857b2',
        'gsi1': True,
        'condition_type': ConditionType.LESS_THAN_OR_EQUAL,
        'condition_value': f'Record#5678',
    }
    mock_crud_service.list_items.assert_called_with(**expected)


def test_list_records_balance_start(processor):
    event = LIST_RECORDS_EVENT_VALID
    event['queryStringParameters'] = {'balance_start': '15'}
    mock_crud_service.list_items.return_value = LIST_RECORDS_CRUD_RETURN_VALUE
    processor.process_list_records_event(event=event)

    expected = {
        'pk': f'User#77d46173-1d59-48d0-8b75-eaa76eb857b2',
        'gsi2': True,
        'condition_type': ConditionType.GREATER_THAN_OR_EQUAL,
        'condition_value': f'Record#15',
    }
    mock_crud_service.list_items.assert_called_with(**expected)


def test_list_records_balance_start_and_balance_end_provided(processor):
    event = LIST_RECORDS_EVENT_VALID
    event['queryStringParameters'] = {'balance_start': '15', 'balance_end': '20'}
    mock_crud_service.list_items.return_value = LIST_RECORDS_CRUD_RETURN_VALUE
    processor.process_list_records_event(event=event)

    expected = {
        'pk': f'User#77d46173-1d59-48d0-8b75-eaa76eb857b2',
        'gsi2': True,
        'condition_type': ConditionType.BETWEEN,
        'low_value': f'Record#15',
        'high_value': f'Record#20'
    }
    mock_crud_service.list_items.assert_called_with(**expected)


def test_list_records_balance_end_only(processor):
    event = LIST_RECORDS_EVENT_VALID
    event['queryStringParameters'] = {'balance_end': '20'}
    mock_crud_service.list_items.return_value = LIST_RECORDS_CRUD_RETURN_VALUE
    processor.process_list_records_event(event=event)

    expected = {
        'pk': f'User#77d46173-1d59-48d0-8b75-eaa76eb857b2',
        'gsi2': True,
        'condition_type': ConditionType.LESS_THAN_OR_EQUAL,
        'condition_value': f'Record#20'
    }
    mock_crud_service.list_items.assert_called_with(**expected)

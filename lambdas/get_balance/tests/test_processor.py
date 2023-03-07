import pytest

from mock import MagicMock
from shared.fixture_utils import json_fixture
from lambdas.get_balance.processor import GetBalanceEventProcessor
from shared.json_utils import json_string_to_dict
from shared.models.record_model import DEFAULT_INITIAL_USER_BALANCE
from shared.user_utils import get_user_id_from_cognito_authorizer

mock_logger = MagicMock()
mock_crud_service = MagicMock()

GET_BALANCE_EVENT_VALID = json_fixture('get_balance_event_valid.json')
LIST_ITEMS_GET_USER_NO_RECORDS_RETURN_VALUE = json_fixture('list_items_get_user_no_records_return_value.json')
LIST_ITEMS_GET_USER_RECORDS_BALANCE_RETURN = json_fixture('list_items_get_user_records_balance_return.json')


def reset_mocks():
    mock_logger.reset_mock()
    mock_crud_service.reset_mock()


@pytest.fixture()
def processor() -> GetBalanceEventProcessor:
    reset_mocks()
    return GetBalanceEventProcessor(logger=mock_logger,
                                    crud_service=mock_crud_service)


def test_get_balance_first_user_operation_returns_default_initial_balance(processor):
    event = GET_BALANCE_EVENT_VALID
    mock_crud_service.list_items.return_value = LIST_ITEMS_GET_USER_NO_RECORDS_RETURN_VALUE
    result = processor.process_get_balance_event(event=event)

    expected = {
        'UserId': get_user_id_from_cognito_authorizer(logger=mock_logger,
                                                      event=event),
        'UserBalance': DEFAULT_INITIAL_USER_BALANCE
    }

    assert json_string_to_dict(result.body) == expected


def test_get_balance_returns_current_balance(processor):
    event = GET_BALANCE_EVENT_VALID
    mock_crud_service.list_items.return_value = LIST_ITEMS_GET_USER_RECORDS_BALANCE_RETURN
    result = processor.process_get_balance_event(event=event)

    expected = {
        'UserId': get_user_id_from_cognito_authorizer(logger=mock_logger,
                                                      event=event),
        'UserBalance': LIST_ITEMS_GET_USER_RECORDS_BALANCE_RETURN[0]['user_balance']
    }

    assert json_string_to_dict(result.body) == expected

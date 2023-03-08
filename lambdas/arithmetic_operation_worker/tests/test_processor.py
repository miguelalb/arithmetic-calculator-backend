import pytest
from mock import MagicMock, patch

from lambdas.arithmetic_operation_worker.processor import ArithmeticOperationWorkerProcessor
from shared.fixture_utils import json_fixture

mock_logger = MagicMock()
mock_crud_service = MagicMock()
mock_js_utc_now = MagicMock()

ARITHMETIC_OPERATION_EVENT_VALID = json_fixture('arithmetic_operation_event_valid.json')
LIST_ITEMS_GET_USER_NO_RECORDS_RETURN_VALUE = json_fixture('list_items_get_user_no_records_return_value.json')
ARITHMETIC_OPERATION_EXPECTED_VALID = json_fixture('arithmetic_operation_expected_valid.json')


def reset_mocks():
    mock_logger.reset_mock()
    mock_crud_service.reset_mock()


@pytest.fixture()
def processor() -> ArithmeticOperationWorkerProcessor:
    reset_mocks()
    return ArithmeticOperationWorkerProcessor(logger=mock_logger,
                                              crud_service=mock_crud_service)


@patch("lambdas.arithmetic_operation_worker.processor.get_js_utc_now", mock_js_utc_now)
def test_arithmetic_operation_success(processor):
    event = ARITHMETIC_OPERATION_EVENT_VALID
    mock_crud_service.list_items.return_value = LIST_ITEMS_GET_USER_NO_RECORDS_RETURN_VALUE
    mock_js_utc_now.return_value = 1678232290113
    processor.process_arithmetic_operation_event(event=event)
    expected = ARITHMETIC_OPERATION_EXPECTED_VALID

    mock_crud_service.create.assert_called_with(**expected)



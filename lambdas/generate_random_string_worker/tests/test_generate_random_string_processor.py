import pytest
from mock import MagicMock, patch
from requests import Response

from shared.fixture_utils import json_fixture
from lambdas.generate_random_string_worker.processor import GenerateRandomStringWorkerProcessor

mock_logger = MagicMock()
mock_crud_service = MagicMock()
mock_request_helper = MagicMock()
mock_cache = MagicMock()
mock_js_utc_now = MagicMock()

GENERATE_RANDOM_STRING_EVENT_VALID = json_fixture('generate_random_string_event_valid.json')
RANDOM_STRING_REQUEST_RETURN_VALUE = "PKXculUm\nWhVZdSjH\nLQaa2XiN\new5KmzQK\nwG953VwV\nkQUnfUhG\nlBo9BIWI\nd4qWQZry\nbSVT7BjF"
RANDOM_STRING_OPERATION_EXPECTED_VALID = json_fixture('random_string_operation_expected_valid.json')


@pytest.fixture(scope="module")
def processor() -> GenerateRandomStringWorkerProcessor:
    return GenerateRandomStringWorkerProcessor(logger=mock_logger,
                                               crud_service=mock_crud_service,
                                               random_org_api_url='',
                                               query_params={},
                                               random_string_cache=mock_cache)


@patch('lambdas.generate_random_string_worker.processor.request_with_retry', mock_request_helper)
@patch("lambdas.generate_random_string_worker.processor.get_js_utc_now", mock_js_utc_now)
def test_generate_random_string_success(processor):
    event = GENERATE_RANDOM_STRING_EVENT_VALID
    mock_crud_service.list_items.return_value = []
    mock_request_helper.text = RANDOM_STRING_REQUEST_RETURN_VALUE
    mock_cache.popitem.return_value = ("PKXculUm", "PKXculUm")
    mock_js_utc_now.return_value = 1678232290113
    processor.process_generate_random_string_event(event=event)

    expected = RANDOM_STRING_OPERATION_EXPECTED_VALID
    mock_crud_service.create.assert_called_with(**expected)

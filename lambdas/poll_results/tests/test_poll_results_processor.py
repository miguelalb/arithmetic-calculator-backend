from http import HTTPStatus

import pytest
from mock import MagicMock

from lambdas.poll_results.processor import PollResultsProcessor
from shared.error_handling import HTTPException
from shared.fixture_utils import json_fixture
from shared.json_utils import json_string_to_dict

mock_logger = MagicMock()
mock_crud_service = MagicMock()

POLL_RESULTS_EVENT_VALID = json_fixture('poll_results_event_valid.json')
POLL_RESULTS_GET_USER_RECORD_RETURN_VALUE = json_fixture('poll_results_get_user_record_return_value.json')
POLL_RESULTS_VALID_EXPECTED = json_fixture('poll_results_valid_expected.json')


def reset_mocks():
    mock_logger.reset_mock()
    mock_crud_service.reset_mock()


@pytest.fixture(scope="module")
def processor() -> PollResultsProcessor:
    reset_mocks()
    return PollResultsProcessor(logger=mock_logger,
                                crud_service=mock_crud_service)


def test_poll_results_success(processor):
    event = POLL_RESULTS_EVENT_VALID
    mock_crud_service.get.return_value = POLL_RESULTS_GET_USER_RECORD_RETURN_VALUE
    result = processor.process_poll_results_event(event=event)

    expected = POLL_RESULTS_VALID_EXPECTED

    assert result.status_code == HTTPStatus.OK
    assert json_string_to_dict(result.body) == expected


def test_poll_results_no_record_raises_404(processor):
    event = POLL_RESULTS_EVENT_VALID
    mock_crud_service.get.return_value = None
    with pytest.raises(HTTPException):
        processor.process_poll_results_event(event=event)

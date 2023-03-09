import pytest
from mock import MagicMock

from shared.error_handling import HTTPException
from shared.fixture_utils import json_fixture
from shared.pagination import Paginator

mock_logger = MagicMock()

PAGINATOR_ITEMS_LIST = json_fixture('paginator_items_list.json')
PAGINATOR_PAGE_ONE_EXPECTED = json_fixture('paginator_page_one_expected.json')
PAGINATOR_PAGE_TWO_EXPECTED = json_fixture('paginator_page_two_expected.json')
PAGINATOR_PAGE_FIVE_EXPECTED = json_fixture('paginator_page_five_expected.json')


def test_paginator_page_one():
    paginator = Paginator(logger=mock_logger,
                          page="1",
                          per_page="2")
    result = paginator.paginate(items_list=PAGINATOR_ITEMS_LIST)

    assert result == PAGINATOR_PAGE_ONE_EXPECTED


def test_paginator_page_two():
    paginator = Paginator(logger=mock_logger,
                          page="2",
                          per_page="2")
    result = paginator.paginate(items_list=PAGINATOR_ITEMS_LIST)

    assert result == PAGINATOR_PAGE_TWO_EXPECTED


def test_paginator_page_five():
    paginator = Paginator(logger=mock_logger,
                          page="5",
                          per_page="2")
    result = paginator.paginate(items_list=PAGINATOR_ITEMS_LIST)

    assert result == PAGINATOR_PAGE_FIVE_EXPECTED


def test_paginator_page_out_of_bounds():
    paginator = Paginator(logger=mock_logger,
                          page="20",
                          per_page="2")
    result = paginator.paginate(items_list=PAGINATOR_ITEMS_LIST)

    assert result == []


def test_paginator_starts_on_page_one():
    with pytest.raises(HTTPException):
        Paginator(logger=mock_logger,
                  page="0",
                  per_page="2")


def test_paginator_per_page_must_be_at_least_one():
    with pytest.raises(HTTPException):
        Paginator(logger=mock_logger,
                  page="1",
                  per_page="0")


def test_paginator_parameter_must_be_numeric():
    with pytest.raises(HTTPException):
        Paginator(logger=mock_logger,
                  page="WORLD",
                  per_page="HELLO")

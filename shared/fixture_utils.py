import importlib
from pathlib import Path
from typing import Union

import simplejson as json

"""
Helper functions to resolve file path location when loading fixtures.
"""


def json_fixture(filename: str) -> Union[dict, list]:
    """Resolving the base path from the module location as opposed to relative to the directory from which
    the test was launched allows more flexibility (e.g. running tests from within an IDE as well as via tox).
    """
    base_path = Path(importlib.util.find_spec('tests').origin).parent.joinpath('resources')
    with base_path.joinpath(filename).open('r') as fixture_data:
        return json.load(fixture_data, encoding='utf-8')

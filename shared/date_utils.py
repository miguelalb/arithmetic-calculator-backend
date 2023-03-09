from datetime import datetime
from http import HTTPStatus
from logging import Logger

from shared.error_handling import HTTPException


def get_js_utc_now() -> int:
    """
    source: https://stackoverflow.com/questions/29736102/convert-python-utc-time-stamp-to-local-time-in-javascript
    Converts a Python utc now timestamp to Javascript equivalent utc timestamp milliseconds value.
    """
    utc_time = datetime.utcnow()
    js_timestamp = (utc_time - datetime(1970, 1, 1)).total_seconds() * 1000
    return int(js_timestamp)


def validate_date_epoch_string(logger: Logger, date: str) -> None:
    """
    Validates is a valid epoch date
    :param logger: logger
    :param date: date to validate
    """
    if not date.isnumeric() or int(date) < 0:
        logger.error(f"Date provided is not a valid {date}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            msg="Date is not a valid epoch date")


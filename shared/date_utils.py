from datetime import datetime


def get_js_utc_now() -> int:
    """
    source: https://stackoverflow.com/questions/29736102/convert-python-utc-time-stamp-to-local-time-in-javascript
    Converts a Python utc now timestamp to Javascript equivalent utc timestamp milliseconds value.
    """
    utc_time = datetime.utcnow()
    js_timestamp = (utc_time - datetime(1970, 1, 1)).total_seconds() * 1000
    return int(js_timestamp)

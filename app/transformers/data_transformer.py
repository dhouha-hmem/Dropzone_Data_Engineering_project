from __future__ import annotations
from datetime import datetime, timezone
from math import isfinite
from statistics import mean, pstdev
from typing import Iterable, Dict, Any, List
from utils.datetime_utils import parse_timestamp_to_utc
from dateutil import parser


class DataQualityError(ValueError):
    """Raised when payload fails data-quality rules """

"""
    Validate timestamp rules :
    - must be a non-empty string
    - must be valid ISO8601
    - must include timezone offset
    Raises DataQualityError if invalid.
"""
def timestamp_quality_check(ts: Any) -> None:

    if not isinstance(ts, str) or not ts.strip():
        raise DataQualityError("time_stamp must be a non-empty string")

    try:
        dt = parser.isoparse(ts)
    except (ValueError, TypeError) as e:
        raise DataQualityError(f"timestamp is not valid ISO8601: {ts}") from e

    if dt.tzinfo is None:
        raise DataQualityError("timestamp must include timezone offset (e.g. -04:00)")



"""
    Data quality checks :
    - must be provided and not be empty
    - all values must be numeric and finite numbers (no NaN/inf)
"""
def _validate_and_clean_data_points(values: Iterable[Any]) -> List[float]:

    if values is None:
        raise DataQualityError("data must be provided")

    cleaned: List[float] = []
    for v in values:
        # Convert value to float
        try:
            f = float(v)
        except (TypeError, ValueError):
            raise DataQualityError(f"data contains a non-numeric value: {v!r}")
        # Reject NaN or infinite values
        if not isfinite(f):
            raise DataQualityError(f"data contains non-finite value (NaN/inf): {v!r}")

        cleaned.append(f)
    # Ensure data array is not empty
    if len(cleaned) == 0:
        raise DataQualityError("data must not be empty")

    return cleaned


"""
    Main transformation logic:
    Input raw JSON payload containing:
      - time_stamp (ISO8601 with timezone offset)
      - data (array of measuring points)
    Output analytics-ready dict:
      - timestamp_utc
      - mean (average of values)
      - std_dev (population standard deviation)
"""
def transform_payload(raw_payload: Dict[str, Any]) -> Dict[str, Any]:

    # Ensure payload is a JSON object
    if not isinstance(raw_payload, dict):
        raise DataQualityError("payload must be a JSON object (dictionary)")
 
    # Extract fields from raw payload
    ts = raw_payload.get("time_stamp")
    data = raw_payload.get("data")

    # validate timestamp quality
    timestamp_quality_check(ts)
     # parse + normalize timestamp to UTC 
    timestamp_utc = parse_timestamp_to_utc(ts)
   
    # Validate and clean data points
    values = _validate_and_clean_data_points(data)

    # Compute aggregations
    m = mean(values)

    # Compute population standard deviation
    # treating the incoming array as a full batch
    s = pstdev(values) if len(values) > 1 else 0.0

    # Return transformed, analytics-ready result
    return {
        "measured_at": timestamp_utc,   
        "mean": m,
        "std_dev": s,
    }

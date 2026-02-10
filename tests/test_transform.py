import math
from datetime import datetime, timezone
import pytest
# Function under test + custom exception
from app.transformers.data_transformer import transform_payload, DataQualityError



"""
    - test valid timestamp WITH timezone
    - test valid numeric data array
    Expect:
    - timestamp converted to UTC
    - correct count, mean, and standard deviation
"""
def test_transform_path():
    payload = {
        "time_stamp": "2019-05-01T06:00:00-04:00",
        "data": [0, 2],
    }

    out = transform_payload(payload)

    # Timestamp is converted to UTC
    assert out["measured_at"] == datetime(2019, 5, 1, 10, 0, 0)
    # Aggregations
    assert out["mean"] == 1.0
    # Use isclose for floating-point safety
    assert math.isclose(out["std_dev"], 1.0, rel_tol=1e-9)



#timestamp without timezone offset should be rejected
def test_transform_rejects_missing_tz():

    payload = {
        # missing timezone offset
        "time_stamp": "2019-05-01T06:00:00",  
        "data": [1, 2],
    }
    #DataQualityError is raised
    with pytest.raises(DataQualityError):
        transform_payload(payload)


""" - all values in data[] must be numeric and finite
 - DataQualityError when non-numeric values are presen"""
def test_transform_rejects_non_numeric():
    """
    Data array containing non-numeric values must be rejected
    """
    payload = {
        "time_stamp": "2019-05-01T06:00:00-04:00",
        "data": [1, "x"],  
    }

    with pytest.raises(DataQualityError):
        transform_payload(payload)


from datetime import datetime, timezone
from dateutil import parser

"""
    Parse an ISO8601 timestamp string with timezone information
    and convert it to a UTC datetime.

    Example:
    "2019-05-01T06:00:00-04:00" -> 2019-05-01 10:00:00 
"""
def parse_timestamp_to_utc(ts: str) -> datetime:
   
   # Parse the timestamp string into a datetime object
    dt = parser.parse(ts)
    # If the timestamp includes timezone information
    if dt.tzinfo is not None:
        # Convert the datetime to UTC and drop tzinfo to store a naive UTC datetime
        
        dt = parser.isoparse(ts).astimezone(timezone.utc).replace(tzinfo=None)

    return dt

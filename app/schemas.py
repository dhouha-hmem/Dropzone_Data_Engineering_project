from typing import List
from pydantic import BaseModel, Field


"""
 This class defines the expected structure of the incoming POST request
 FastAPI uses this schema to:
 - validate and parse the JSON body
 - generate OpenAPI (Swagger documentation)"""
class IngestRequest(BaseModel):
    # time_stamp must be:
    # - required field
    # - of type string
    # - expected to follow ISO8601 format including timezone offset
    time_stamp: str = Field(
        ...,                  
        description="ISO8601 timestamp including timezone offset")
    # Array of numeric measurement values
    # Must be present and contain numbers only
    data: List[float] = Field(
        ..., 
        description="Array of measuring points")


""" Defines the response returned by POST /ingest.
 This documents and enforces the response shape."""
class IngestResponse(BaseModel):
    # Status of the ingestion request
    status: str
    # Unique identifier of the stored raw payload
    raw_id: str


""" Defines the response returned by POST /process.
 Provides a summary of batch processing results."""
class ProcessResponse(BaseModel):
    # Number of payloads successfully transformed and stored
    processed: int

    # Number of payloads that failed validation or transformation
    failed: int

    # Total number of raw files that were inspected
    checked: int







# Load environment variables from .env file
# This allows configuration (API key, DB URL) 
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
# Pydantic schemas defining request and response contracts
from app.schemas import IngestRequest, ProcessResponse, IngestResponse

# Business logic for transforming incoming payloads
from app.transformers.data_transformer import transform_payload, DataQualityError

from app.storage.storage_silver import init_db, upsert_transformed
from app.storage.storage_bronze import save_raw, list_raw_files, read_raw_file
# API key authentication dependency
from app.security import require_api_key


'''
 Initialize database at application startup using FastAPI lifespan
 ensure the database schema is initialized before handling requests
'''
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables if they do not exist
    init_db()
    yield

# FastAPI application instance
app = FastAPI(
    title="Dropzone Challenge API",
    version="1.0.0",
    description="Ingest JSON payloads, store raw data, transform and store analytics-ready results.",
    lifespan=lifespan
)

'''
Health check endpoint
Used to verify that the API is running and reachable
'''
@app.get("/health")
def health():
    return {"status": "ok"}



'''
 Ingest endpoint
 - Accepts a validated JSON payload
 - Stores it immediately as raw data 
 - Returns HTTP 202 (Accepted) because processing is asynchronous
 - Secured using an API key
'''
@app.post("/ingest", status_code=202, response_model=IngestResponse, dependencies=[Depends(require_api_key)])
def ingest(payload: IngestRequest) -> IngestResponse:
    # Persist raw payload immediately to avoid data loss
    raw_id = save_raw(payload.model_dump())
    # Return acknowledgement with reference ID
    return {"status": "accepted", "raw_id": raw_id}

'''
 Process endpoint
 - Reads raw payloads from disk
 - Transforms valid payloads
 - Stores transformed results in the database
 - Counts processed vs failed records
 - Secured using an API key
'''
@app.post("/process", response_model=ProcessResponse, dependencies=[Depends(require_api_key)])
def process(limit: int = 100):
    # Retrieve a batch of raw files to process
    files = list_raw_files(limit=limit)
    processed = 0
    failed = 0

    # Process each raw payload independently
    for filename in files:
        payload = read_raw_file(filename)
        try:
            transformed = transform_payload(payload)
            upsert_transformed(transformed)
            processed += 1
        except DataQualityError:
            # Invalid data is counted but kept for debugging
            failed += 1  
    # Return processing summary
    return {"processed": processed, "failed": failed, "checked": len(files)}



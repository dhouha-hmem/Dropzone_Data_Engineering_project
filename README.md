# Dropzone Challenge – Data Engineering  

A REST API that ingests JSON payloads, stores raw data immediately as JSON files, then processes stored raw files to compute analytics-ready aggregations and upserts results into PostgreSQL.



## What this service does

### Mandatory tasks
- **01 – Data ingestion**  
  `POST /ingest` accepts JSON payloads and returns `202 Accepted` + a `raw_id`.

- **02 – Store raw data immediately**  
  The API persists each incoming payload immediately as a JSON file on the filesystem:
<DROPZONE_RAW_DIR>/<uuid>.json (defaults to data/raw).
The raw files act as a staging area for later processing by `/process`.

- **03 – Data transformation**  
  Converts `time_stamp` to **UTC** (timezone required), validates numeric values, then computes:
  - `timestamp_utc`
  - `mean`
  - `std_dev` (population stdev)

- **04 – Store transformed data**  
  Writes results to Postgres table `measurements` using **UPSERT**:
  - `timestamp_utc` is the **primary key**
  - if same timestamp arrives again → overwrite `mean` and `std_dev`

### Optional features implemented
- **Testing**: pytest tests for API + transform + Postgres storage
- **Security (API key)**: simple header-based authentication with `x-api-key`
- **OpenAPI (Swagger documentation)**: FastAPI auto-generates docs at `/docs`
- **Scalability**: ingestion is decoupled from transformation (/ingest vs /process), enabling independent scaling of processing without slowing ingestion

---

## Project structure

```
├── app/
│   ├── main.py                 # FastAPI app + endpoints (/health, /ingest, /process)
│   ├── schemas.py              # Pydantic request/response models
│   ├── security.py             # API key auth dependency (x-api-key header)
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── storage_bronze.py   # Raw JSON file storage 
│   │   └── storage_silver.py   # Postgres table init + upsert 
│   └── transformers/
│       ├── __init__.py
│       └── data_transformer.py # Data quality checks + transformation 
│
├── utils/
│   ├── __init__.py
│   └── datetime_utils.py       # Timestamp parsing helpers (UTC normalization)
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py             # API endpoint tests 
│   ├── test_storage.py         # Postgres storage tests 
│   └── test_transform.py       # Unit tests for transformation + data quality rules
│
├── data/
│   └── raw/                    # Default raw payload folder (local dev)
│
├── payload.json                # Example input payload
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest config (adds project root to python path)
└── README.md
```

## Requirements

- Python 3.11+
- PostgreSQL 
- Recommended: create a virtual environment



## Setup

### 1) Create venv + install dependencies

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# or Git Bash:
source .venv/Scripts/activate

pip install -r requirements.txt
```

### 2) Configuration (Environment Variables)

This project is configured using environment variables.
For local development, they can be defined in a .env file located at the project root.


- API security: DROPZONE_API_KEY=some-secret

- Postgres connection (required for DB persistence + test_storage): 
DROPZONE_DATABASE_URL=postgresql://user:password@localhost:5432/dropzone

- Raw dropzone directory (optional): DROPZONE_RAW_DIR=data/raw

#### Notes: 

- If DROPZONE_API_KEY is set, all API requests must include the header: x-api-key: some-secret

- If DROPZONE_API_KEY is not set, the API runs without authentication.

- DROPZONE_RAW_DIR defaults to data/raw if not provided.

## Run the API

Start the FastAPI application with:

```
uvicorn app.main:app --reload
```

The API will be available at:

- Health check: GET /health

- Swagger UI: http://127.0.0.1:8000/docs

## API Usage
### 1) Ingest (store raw data immediately)

This endpoint accepts data and immediately stores the raw payload on disk.
Processing is intentionally decoupled.

cURL example:
```
curl -X POST "http://127.0.0.1:8000/ingest" \
  -H "Content-Type: application/json" \
  -H "x-api-key: secret" \
  -d @payload.json
```

A file is created immediately at:  ```data/raw/<raw_id>.json```

### 2) Process (transform + store to Postgres)

This endpoint reads raw JSON files from the dropzone directory,
applies data quality checks and transformations, and upserts results into Postgres.

cURL example:
```
curl -X POST "http://127.0.0.1:8000/process" \
  -H "x-api-key: secret" \
```
#### Data Quality Rules (Transformation)

A payload is rejected (DataQualityError) if:

- time_stamp is missing or not valid 
- time_stamp does not include a timezone offset
- data is missing or empty
- Any value in data is non-numeric, NaN, or infinite

## Tests
Run all tests with: ```pytest -v```

### Test groups
test_transform.py:

- Pure unit tests (No database required)

test_api.py:

- Uses pytest tmp_path and monkeypatch

- Raw files are written to a temporary directory

- Database writes are mocked 

test_storage.py:

- Requires a running Postgres instance

- Uses DROPZONE_DATABASE_URL

- Automatically skipped if DB is not configured

Pytest automatically removes test directories after the test session.

## Security (API Key)

Authentication is enforced via an API key mechanism, using a header check:

- Header: x-api-key

- Expected value: DROPZONE_API_KEY

This approach is intentionally simple for the challenge and can be extended to:

- Token-based authentication (OAuth2 / JWT)

- Rate limiting

- Request logging and audit trails

## Future improvements
Potential extensions to this solution:
- Remove raw files after successful processing (queue semantics)

- Add structured logging and request IDs

- Add Docker Compose for API + Postgres

- Add CI workflow ..


import json
from pathlib import Path
# FastAPI test client used to call API endpoints without running a real server
from fastapi.testclient import TestClient
# Import the FastAPI app to test
from app.main import app
import app.main as main_module  


# API key used for authentication in tests
API_KEY = "secret"


# Helper function that returns the authentication headers
# expected by the API (x-api-key)
def _auth_headers():
    return {"x-api-key": API_KEY}



"""
    Test the /ingest endpoint:
    - returns HTTP 202 Accepted
    - returns a raw_id in the response
    - stores the raw payload as a JSON file on disk
      in <DROPZONE_RAW_DIR>/<raw_id>.json
"""
def test_ingest_stores_raw(tmp_path, monkeypatch):

    # Use temp raw directory 
    raw_dir = tmp_path / "raw"
    monkeypatch.setenv("DROPZONE_RAW_DIR", str(raw_dir))

    # Enable API key authentication for this test
    monkeypatch.setenv("DROPZONE_API_KEY", API_KEY)

    # Valid payload with ISO8601 timestamp including timezone
    payload = {"time_stamp": "2019-05-01T06:00:00-04:00", "data": [0, 2]}

    # Use TestClient to call the API endpoint
    with TestClient(app) as client:
        r = client.post("/ingest", json=payload, headers=_auth_headers())

    # Verify HTTP response
    assert r.status_code == 202
    # Verify response body
    body = r.json()
    assert body["status"] == "accepted"
    assert "raw_id" in body
    # Verify that the raw payload was stored on disk
    raw_id = body["raw_id"]
    raw_file = Path(raw_dir) / f"{raw_id}.json"
    assert raw_file.exists()

    # Verify stored content matches original payload
    stored = json.loads(raw_file.read_text(encoding="utf-8"))
    assert stored == payload


    """
    Test the /process endpoint when a bad payload exists.
    - ingest a payload with an invalid timestamp (no timezone)
    - /process should fail transformation
    - failed count should increase
    - processed count should remain zero

    We mock DB writes to avoid needing Postgres
    """
def test_process_counts_failed(tmp_path, monkeypatch):

    # Create isolated temp directory for raw files
    raw_dir = tmp_path / "raw"
    monkeypatch.setenv("DROPZONE_RAW_DIR", str(raw_dir))

    # Enable API key authentication for this test
    monkeypatch.setenv("DROPZONE_API_KEY", API_KEY)

    # Mock DB write function so no real database is required
    monkeypatch.setattr(main_module, "upsert_transformed", lambda row: None)

    bad_payload = {"time_stamp": "2019-05-01T06:00:00", "data": [0, 2]}  

    with TestClient(app) as client:
        # Ingest accepts raw payload even if data is invalid
        r1 = client.post("/ingest", json=bad_payload, headers=_auth_headers())
        assert r1.status_code == 202
        # Process attempts transformation and should fail
        r2 = client.post("/process", headers=_auth_headers())
        assert r2.status_code == 200
        out = r2.json()

    # Verify processing results
    assert out["failed"] == 1
    assert out["processed"] == 0
    assert out["checked"] >= 1



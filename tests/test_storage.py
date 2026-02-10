import os
from datetime import datetime, timezone
# PostgreSQL driver used to verify stored data
import psycopg
import pytest
# Functions under test
from app.storage.storage_silver import init_db, upsert_transformed


"""
    Test helper:
    - reads DB url from env
    - Skips storage tests entirely if no database is configured
"""
def _db_url() -> str:

    url = os.getenv("DROPZONE_DATABASE_URL")
    if not url:
        pytest.skip("DROPZONE_DATABASE_URL not set -> skipping Postgres storage tests")
    return url

"""
Database connectivity smoke test
- verify PostgreSQL is reachable
- SQL queries can be executed
"""
def test_db_connection_works():

    with psycopg.connect(_db_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            assert cur.fetchone()[0] == 1

"""
Fixture: clean database before each test
- ensures database schema is initialized
- measurements table is truncated
- tests always start from a clean state
"""
@pytest.fixture
def clean_db():

    # Ensure table exists
    init_db()
    # Remove all existing rows
    with psycopg.connect(_db_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE measurements;")
        conn.commit()


"""
    Verify UPSERT behavior in Postgres:
    - inserting a row with a new timestamp creates a record
    - inserting again with the same timestamp replaces the existing record
    - timestamp_utc acts as the primary key
"""
def test_upsert_replaces_existing(clean_db):


    # Define a fixed UTC timestamp
    ts = datetime(2019, 5, 1, 10, 0, 0)

    # First insert
    upsert_transformed({"measured_at": ts, "mean": 1.0, "std_dev": 2.0})

    # Second insert with same PK, should overwrite values
    upsert_transformed({"measured_at": ts, "mean": 9.0, "std_dev": 8.0})

    # Read stored data directly from Postgres
    with psycopg.connect(_db_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT measured_at, mean, std_dev FROM measurements;")
            row = cur.fetchone()

    # Validate that the second insert replaced the first one
    assert row[0] == ts     # timestamp unchanged
    assert row[1] == 9.0    # mean overwritten
    assert row[2] == 8.0    # std_dev overwritten

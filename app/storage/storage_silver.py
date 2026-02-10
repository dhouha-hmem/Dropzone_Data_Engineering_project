from __future__ import annotations
from typing import Dict, Any
import os
# PostgreSQL driver
import psycopg
from psycopg.rows import dict_row

"""
 Database configuration

 Returns the PostgreSQL connection string from environment variables.
 Example: postgresql://user:password@localhost:5432/dropzone
"""
def _db_url() -> str:

    return os.getenv("DROPZONE_DATABASE_URL", "")

"""
 Creates and returns a new PostgreSQL connection.
 - Fails fast if the database URL is not configured
 - Uses dict_row so query results can be accessed by column name
"""
def _get_conn() -> psycopg.Connection:
    db_url = _db_url()
    # Ensure database URL is provided
    if not db_url:
        raise RuntimeError(
            "DROPZONE_DATABASE_URL is not set. "
            "Example: postgresql://postgres:postgres@localhost:5432/dropzone"
        )

    return psycopg.connect(db_url, row_factory=dict_row)

"""
 Schema initialization
 - Creates the measurements table if it does not exist
 - Uses timestamp_utc as the primary key
 - Executed once at application startup
"""
def init_db() -> None:
    
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS measurements (
                    measured_at TIMESTAMP PRIMARY KEY,
                    mean DOUBLE PRECISION NOT NULL,
                    std_dev DOUBLE PRECISION NOT NULL
                )
                """
            )
        conn.commit()


"""
Inserts or updates a transformed measurement.
 - If timestamp_utc does NOT exist -> insert a new row
 - If timestamp_utc already exists -> overwrite mean & std_dev
"""
def upsert_transformed(row: Dict[str, Any]) -> None:
    
    # Extract and normalize values
    ts = row["measured_at"]
    mean_val = float(row["mean"])
    std_val = float(row["std_dev"])

    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO measurements (measured_at, mean, std_dev)
                VALUES (%s, %s, %s)
                ON CONFLICT (measured_at) DO UPDATE
                SET mean = EXCLUDED.mean,
                    std_dev = EXCLUDED.std_dev
                """,
                (ts, mean_val, std_val),
            )
        conn.commit()

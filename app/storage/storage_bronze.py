import json
import os
import uuid
from typing import Any, Dict, List

"""
 Raw storage configuration

 Returns the directory where raw payloads are stored:
 - Uses environment variable if set 
 - Falls back to 'data/raw' by default
"""
def _raw_dir() -> str:
    return os.getenv("DROPZONE_RAW_DIR", os.path.join("data", "raw"))


# Ensures that the raw storage directory exists.
# Creates the directory if it does not exist
def init_raw_dir() -> None:
    os.makedirs(_raw_dir(), exist_ok=True)

"""
 Saves the incoming raw payload to disk as a JSON file.
 - Generates a unique identifier (UUID)
 - Writes payload immediately to avoid data loss
 - Returns the generated raw_id for tracking"""
def save_raw(payload: Dict[str, Any]) -> str:
    """Save payload as a JSON file, return filename (id)."""
    init_raw_dir()
    raw_id = str(uuid.uuid4())
    path = os.path.join(_raw_dir(), f"{raw_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return raw_id

# Lists raw payload files waiting to be processed
# Limited to avoid processing too many files at once
def list_raw_files(limit: int = 100) -> List[str]:
    init_raw_dir()
    files = [f for f in os.listdir(_raw_dir()) if f.endswith(".json")]
    files.sort()
    return files[:limit]

# Reads and returns a raw payload 
def read_raw_file(filename: str) -> Dict[str, Any]:
    path = os.path.join(_raw_dir(), filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


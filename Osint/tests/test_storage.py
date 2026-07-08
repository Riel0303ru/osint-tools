import os
# Force testing to use local SQLite database
os.environ["DATABASE_URL"] = "sqlite:///tests/test_storage_history.db"

import pytest
from core.base.storage import Storage, ScanResultModel
from core.base.scan_result import ScanResult

def test_storage_sqlite_init():
    os.makedirs("tests", exist_ok=True)
    db_path = "tests/test_storage_history.db"
    
    storage = Storage(db_path=db_path)
    assert storage.engine is not None
    
    # Dispose connection pool to release lock
    storage.engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)

def test_save_and_get_scan():
    os.makedirs("tests", exist_ok=True)
    db_path = "tests/test_storage_history.db"
    storage = Storage(db_path=db_path)
    
    results = [
        ScanResult(
            platform="TestPlatform",
            username="testuser",
            status="FOUND",
            status_code=200,
            url="http://test.com/user",
            confidence=0.9,
            intelligence_score=15.0,
            extra={"key": "val"}
        )
    ]
    
    timestamp = storage.save_scan("testuser", results)
    assert timestamp is not None
    
    history = storage.get_paginated_history(page=1, limit=10)
    assert len(history) > 0
    assert history[0] == "testuser"
    
    delta = storage.get_delta("testuser", results)
    assert isinstance(delta, list)
    
    storage.engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)

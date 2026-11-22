from concurrent.futures import ThreadPoolExecutor
import sqlite3
import threading

import core.vector_store as vector_store


def test_workspace_write_transaction_serializes_concurrent_mutations(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_store, "VECTOR_PATH", str(tmp_path))
    counter_db = tmp_path / "counter.sqlite3"
    with sqlite3.connect(counter_db) as connection:
        connection.execute("CREATE TABLE counter (value INTEGER NOT NULL)")
        connection.execute("INSERT INTO counter VALUES (0)")

    entered = 0
    entered_lock = threading.Lock()

    def increment(_):
        nonlocal entered
        with vector_store._workspace_write_transaction("workspace-a"):
            with entered_lock:
                entered += 1
            with sqlite3.connect(counter_db, timeout=10) as connection:
                value = connection.execute("SELECT value FROM counter").fetchone()[0]
                connection.execute("UPDATE counter SET value = ?", (value + 1,))

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(increment, range(32)))

    with sqlite3.connect(counter_db) as connection:
        assert connection.execute("SELECT value FROM counter").fetchone()[0] == 32
    assert entered == 32


def test_workspace_write_transaction_rolls_back_and_releases_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_store, "VECTOR_PATH", str(tmp_path))

    try:
        with vector_store._workspace_write_transaction("workspace-a"):
            raise RuntimeError("simulated failed mutation")
    except RuntimeError:
        pass

    with vector_store._workspace_write_transaction("workspace-a"):
        assert True

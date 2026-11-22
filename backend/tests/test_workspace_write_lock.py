from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing
import sqlite3
import threading
import time

import core.vector_store as vector_store


def test_workspace_write_transaction_serializes_concurrent_mutations(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_store, "VECTOR_PATH", str(tmp_path))
    counter_db = tmp_path / "counter.sqlite3"
    with sqlite3.connect(counter_db) as connection:
        connection.execute("CREATE TABLE counter (value INTEGER NOT NULL)")
        connection.execute("INSERT INTO counter VALUES (0)")

    active = 0
    max_active = 0
    entered_lock = threading.Lock()

    def increment(_):
        nonlocal active, max_active
        with vector_store._workspace_write_transaction("workspace-a"):
            with entered_lock:
                active += 1
                max_active = max(max_active, active)
            try:
                time.sleep(0.002)
                with sqlite3.connect(counter_db, timeout=10) as connection:
                    value = connection.execute("SELECT value FROM counter").fetchone()[0]
                    connection.execute("UPDATE counter SET value = ?", (value + 1,))
            finally:
                with entered_lock:
                    active -= 1

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(increment, range(32)))

    with sqlite3.connect(counter_db) as connection:
        assert connection.execute("SELECT value FROM counter").fetchone()[0] == 32
    assert max_active == 1


def test_workspace_write_transaction_rolls_back_and_releases_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_store, "VECTOR_PATH", str(tmp_path))

    try:
        with vector_store._workspace_write_transaction("workspace-a"):
            raise RuntimeError("simulated failed mutation")
    except RuntimeError:
        pass

    with vector_store._workspace_write_transaction("workspace-a"):
        assert True



def _increment_counter_in_process(args):
    root_path, counter_path = args
    import core.vector_store as process_vector_store

    process_vector_store.VECTOR_PATH = root_path
    with process_vector_store._workspace_write_transaction("workspace-process"):
        with sqlite3.connect(counter_path, timeout=10) as connection:
            value = connection.execute("SELECT value FROM counter").fetchone()[0]
            connection.execute("UPDATE counter SET value = ?", (value + 1,))
    return True


def test_workspace_write_transaction_serializes_separate_processes(tmp_path):
    counter_db = tmp_path / "process-counter.sqlite3"
    with sqlite3.connect(counter_db) as connection:
        connection.execute("CREATE TABLE counter (value INTEGER NOT NULL)")
        connection.execute("INSERT INTO counter VALUES (0)")

    context = multiprocessing.get_context("spawn")
    args = [(str(tmp_path), str(counter_db)) for _ in range(12)]
    with ProcessPoolExecutor(max_workers=4, mp_context=context) as executor:
        assert all(executor.map(_increment_counter_in_process, args))

    with sqlite3.connect(counter_db) as connection:
        assert connection.execute("SELECT value FROM counter").fetchone()[0] == 12

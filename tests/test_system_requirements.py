"""Tests for the system requirements in section 9 of BACKLOG.md.

Only the requirements that no other test file checks are here.
"""

import ast
import os
import random
import sys
import time
from pathlib import Path

import pytest
from pykv import Database

LOG_SIZE = 1_000_000
READS = 1_000


@pytest.fixture
def db(tmp_path):
    """Each test gets its own database in a temporary file."""
    return Database(tmp_path / "test_data.txt")


@pytest.fixture(scope="module")
def big_log(tmp_path_factory):
    """A log with one million records, shared because it takes time to write."""
    path = tmp_path_factory.mktemp("big") / "big_log.txt"
    with open(path, "wb") as f:
        for i in range(LOG_SIZE):
            f.write(f"key_{i},value_{i}\n".encode("utf-8"))
    return path


def test_sr_06_2_delete_of_unknown_key_writes_nothing(db):
    """SR-06.2: deleting a key that does not exist does not touch the log."""
    # Arrange
    db.set("a", "1")
    size_before = os.path.getsize(db.path)

    # Act
    db.delete("ghost")

    # Assert
    assert os.path.getsize(db.path) == size_before


def test_sr_06_5_runtime_code_only_uses_the_standard_library():
    """SR-06.5: pykv imports nothing outside the Python standard library."""
    # Arrange
    package = Path(__file__).resolve().parent.parent / "pykv"
    imported = set()

    # Act
    for source in package.glob("*.py"):
        for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                imported.add(node.module.split(".")[0])

    # Assert
    assert imported <= set(sys.stdlib_module_names) | {"pykv"}


def test_sr_05_1_set_appends_one_utf8_line(db):
    """SR-05.1: set adds exactly one key,value line encoded in UTF-8."""
    # Arrange
    db.set("a", "1")

    # Act
    db.set("ñandú", "Привет")

    # Assert
    with open(db.path, "rb") as f:
        assert f.read() == "a,1\nñandú,Привет\n".encode("utf-8")


def test_sr_05_2_update_keeps_the_previous_bytes(db):
    """SR-05.2: updating a key leaves everything already written untouched."""
    # Arrange
    db.set("a", "old")
    with open(db.path, "rb") as f:
        before = f.read()

    # Act
    db.set("a", "new")

    # Assert
    with open(db.path, "rb") as f:
        after = f.read()
    assert after == before + b"a,new\n"


def test_sr_05_3_delete_appends_a_tombstone(db):
    """SR-05.3: delete adds a tombstone line and keeps the history."""
    # Arrange
    db.set("a", "1")

    # Act
    db.delete("a")

    # Assert
    with open(db.path, "rb") as f:
        assert f.read() == b"a,1\na,__DELETED__\n"


def test_sr_05_4_log_keeps_the_order_of_the_operations(db):
    """SR-05.4: read from start to end, the log shows the operations in order."""
    # Arrange
    db.set("a", "1")
    db.set("b", "2")

    # Act
    db.set("a", "3")
    db.delete("b")

    # Assert
    with open(db.path, "rb") as f:
        assert f.read().splitlines() == [
            b"a,1",
            b"b,2",
            b"a,3",
            b"b,__DELETED__",
        ]


def test_sr_02_1_index_stores_the_byte_offset_of_the_last_record(db):
    """SR-02.1: the index points to the first byte of the latest record."""
    # Arrange
    db.set("ñ", "ñ")  # 6 bytes in UTF-8: the offset must count bytes, not letters
    db.set("b", "2")

    # Act
    db.set("ñ", "3")

    # Assert
    assert db.index == {"ñ": 10, "b": 6}


def test_sr_02_2_get_reads_only_the_record_of_the_key(db):
    """SR-02.2: get jumps to the record and does not read the rest of the log."""
    # Arrange
    db.set("a", "1")
    db.set("b", "2")
    with open(db.path, "r+b") as f:
        f.write(b"\xff\xff\xff\xff")  # The record of "a" can no longer be decoded

    # Act
    value = db.get("b")

    # Assert
    assert value == "2"


def test_sr_02_3_delete_removes_the_key_from_the_index(db):
    """SR-02.3: a deleted key disappears from the index."""
    # Arrange
    db.set("a", "1")

    # Act
    db.delete("a")

    # Assert
    assert "a" not in db.index


def test_sr_02_5_get_is_fast_with_one_million_keys(big_log):
    """SR-02.5: with 1,000,000 keys, the p99 of get is under 500 ms."""
    # Arrange
    db = Database(big_log)
    keys = [f"key_{random.randrange(LOG_SIZE)}" for _ in range(READS)]
    times = []

    # Act
    for key in keys:
        start = time.perf_counter()
        db.get(key)
        times.append(time.perf_counter() - start)

    # Assert
    assert sorted(times)[int(READS * 0.99)] < 0.5


def test_sr_03_4_failed_write_raises_and_keeps_the_index(db):
    """SR-03.4: if the log cannot be written, set raises and changes nothing."""
    # Arrange
    db.set("a", "1")
    index_before = dict(db.index)
    os.remove(db.path)
    os.mkdir(db.path)  # A folder: opening it to write fails on every system

    # Act / Assert
    with pytest.raises(OSError):
        db.set("b", "2")
    assert db.index == index_before


def test_sr_03_5_opens_one_million_records_in_under_5_seconds(big_log):
    """SR-03.5: rebuilding the index of 1,000,000 records takes under 5 s."""
    # Arrange
    start = time.perf_counter()

    # Act
    db = Database(big_log)
    elapsed = time.perf_counter() - start

    # Assert
    assert len(db.index) == LOG_SIZE
    assert elapsed < 5

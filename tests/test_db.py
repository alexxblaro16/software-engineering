import os
import pytest
import db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Fixture to isolate each test in a temporary database file."""
    test_file = tmp_path / "test_data.txt"
    monkeypatch.setattr(db, "DB_FILE", str(test_file))
    db.INDEX.clear()
    yield
    db.INDEX.clear()


def test_set_and_get(temp_db):
    """Check that a key can be inserted and read correctly."""
    db.set("greeting", "Hello")
    assert db.get("greeting") == "Hello"


def test_update_value(temp_db):
    """Check that modifying a key retrieves the most recent value."""
    db.set("status", "active")
    db.set("status", "updated")
    assert db.get("status") == "updated"


def test_delete_with_tombstone(temp_db):
    """Check that logical deletion (tombstone) removes the key from the index."""
    db.set("temp", "data")
    assert db.get("temp") == "data"
    db.delete("temp")
    assert db.get("temp") is None


def test_utf8_encoding_and_cyrillic(temp_db):
    """Check robust UTF-8 support with international characters (e.g., Russian)."""
    db.set("cliente_ÐœÐ¾ÑÐºÐ²Ð°", "ÐŸÑ€Ð¸Ð²ÐµÑ‚, Ð¼Ð¸Ñ€")
    assert db.get("cliente_ÐœÐ¾ÑÐºÐ²Ð°") == "ÐŸÑ€Ð¸Ð²ÐµÑ‚, Ð¼Ð¸Ñ€"


def test_non_existent_key(temp_db):
    """Check that searching for a non-existent key returns None."""
    assert db.get("key_que_no_existe") is None


def test_independent_keys(temp_db):
    """Check that multiple independent keys do not interfere with each other."""
    db.set("k1", "v1")
    db.set("k2", "v2")
    assert db.get("k1") == "v1"
    assert db.get("k2") == "v2"


def test_set_after_delete(temp_db):
    """Check that a key can be set again after being deleted."""
    db.set("session", "active")
    db.delete("session")
    assert db.get("session") is None
    db.set("session", "restarted")
    assert db.get("session") == "restarted"


def test_append_only_growth(temp_db):
    """Check that the log file grows and never shrinks on updates."""
    db.set("a", "1")
    size_initial = os.path.getsize(db.DB_FILE)
    db.set("a", "2")
    size_after_update = os.path.getsize(db.DB_FILE)
    assert size_after_update > size_initial


def test_delete_non_existent_key(temp_db):
    """Check that deleting a non-existent key does nothing or fails safely without creating file errors."""
    db.delete("ghost_key")
    assert db.get("ghost_key") is None


def test_byte_offsets_multibyte(temp_db):
    """Check byte-offset indexing with multibyte characters."""
    db.set("spanish", "espaÃ±a")
    db.set("chinese", "ä¸­æ–‡")
    assert db.get("spanish") == "espaÃ±a"
    assert db.get("chinese") == "ä¸­æ–‡"


def test_build_index_recovery(temp_db):
    """Check that build_index recovers the latest value after a simulated restart."""
    db.set("k", "v1")
    db.set("k", "v2")
    # Simulate restart by clearing memory index and rebuilding from disk log
    db.INDEX.clear()
    db.build_index()
    assert db.get("k") == "v2"


def test_build_index_respects_tombstones(temp_db):
    """Check that build_index correctly ignores deleted keys via tombstones."""
    db.set("k", "v1")
    db.delete("k")
    db.INDEX.clear()
    db.build_index()
    assert db.get("k") is None


def test_build_index_missing_file(temp_db, monkeypatch):
    """Check that build_index handles a non-existent database file gracefully."""
    monkeypatch.setattr(db, "DB_FILE", "non_existent_file_abc123.txt")
    db.INDEX.clear()
    db.build_index()
    assert db.INDEX == {}
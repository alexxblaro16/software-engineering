import os
import pytest
from pykv import Database


@pytest.fixture
def db(tmp_path):
    """Each test gets its own database in a temporary file."""
    return Database(tmp_path / "test_data.txt")


def test_set_and_get(db):
    """Check that a key can be inserted and read correctly."""
    db.set("greeting", "Hello")
    assert db.get("greeting") == "Hello"


def test_update_value(db):
    """Check that modifying a key retrieves the most recent value."""
    db.set("status", "active")
    db.set("status", "updated")
    assert db.get("status") == "updated"


def test_delete_with_tombstone(db):
    """Check that logical deletion (tombstone) removes the key from the index."""
    db.set("temp", "data")
    assert db.get("temp") == "data"
    db.delete("temp")
    assert db.get("temp") is None


def test_utf8_encoding_and_cyrillic(db):
    """Check robust UTF-8 support with international characters (e.g., Russian)."""
    db.set("cliente_Москва", "Привет, мир")
    assert db.get("cliente_Москва") == "Привет, мир"


def test_non_existent_key(db):
    """Check that searching for a non-existent key returns None."""
    assert db.get("key_que_no_existe") is None


def test_independent_keys(db):
    """Check that multiple independent keys do not interfere with each other."""
    db.set("k1", "v1")
    db.set("k2", "v2")
    assert db.get("k1") == "v1"
    assert db.get("k2") == "v2"


def test_set_after_delete(db):
    """Check that a key can be set again after being deleted."""
    db.set("session", "active")
    db.delete("session")
    assert db.get("session") is None
    db.set("session", "restarted")
    assert db.get("session") == "restarted"


def test_append_only_growth(db):
    """Check that the log file grows and never shrinks on updates."""
    db.set("a", "1")
    size_initial = os.path.getsize(db.path)
    db.set("a", "2")
    size_after_update = os.path.getsize(db.path)
    assert size_after_update > size_initial


def test_delete_non_existent_key(db):
    """Check that deleting a non-existent key fails safely without errors."""
    db.delete("ghost_key")
    assert db.get("ghost_key") is None


def test_byte_offsets_multibyte(db):
    """Check byte-offset indexing with multibyte characters."""
    db.set("spanish", "españa")
    db.set("chinese", "中文")
    assert db.get("spanish") == "españa"
    assert db.get("chinese") == "中文"


def test_build_index_recovery(db):
    """Check that the index recovers the latest value after a restart."""
    db.set("k", "v1")
    db.set("k", "v2")
    # Simulate a restart by opening the same file again
    reopened = Database(db.path)
    assert reopened.get("k") == "v2"


def test_build_index_respects_tombstones(db):
    """Check that rebuilding the index ignores deleted keys via tombstones."""
    db.set("k", "v1")
    db.delete("k")
    reopened = Database(db.path)
    assert reopened.get("k") is None


def test_build_index_missing_file(tmp_path):
    """Check that opening a database whose file does not exist creates it."""
    # Arrange
    path = tmp_path / "non_existent_file.txt"

    # Act
    db = Database(path)

    # Assert
    assert path.exists()
    assert db.index == {}


def test_build_index_many_keys_with_multibyte(db):
    """Check that offsets stay right after a restart with many multibyte keys."""
    # Arrange
    for i in range(100):
        db.set(f"clave_{i}", f"valor_ñ_Привет_{i}")

    # Act
    reopened = Database(db.path)

    # Assert
    assert reopened.get("clave_0") == "valor_ñ_Привет_0"
    assert reopened.get("clave_99") == "valor_ñ_Привет_99"

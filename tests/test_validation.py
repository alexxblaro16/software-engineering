import os
import pytest
from pykv import Database


@pytest.fixture
def db(tmp_path):
    """Each test gets its own database in a temporary file."""
    return Database(tmp_path / "test_data.txt")


def test_key_with_comma_is_rejected(db):
    """Check that a key with a comma raises a clear error."""
    # Arrange
    key = "city,country"

    # Act / Assert
    with pytest.raises(ValueError, match="commas"):
        db.set(key, "Madrid")


def test_key_with_line_break_is_rejected(db):
    """Check that a key with a line break raises a clear error."""
    # Arrange
    key = "first\nsecond"

    # Act / Assert
    with pytest.raises(ValueError, match="line breaks"):
        db.set(key, "value")


def test_empty_key_is_rejected(db):
    """Check that an empty key raises a clear error."""
    # Arrange
    key = ""

    # Act / Assert
    with pytest.raises(ValueError, match="empty"):
        db.set(key, "value")


def test_key_that_is_not_a_string_is_rejected(db):
    """Check that a number used as a key raises a TypeError."""
    # Arrange
    key = 42

    # Act / Assert
    with pytest.raises(TypeError, match="string"):
        db.get(key)


def test_rejected_key_writes_nothing(db):
    """Check that a rejected key leaves the log file untouched."""
    # Arrange
    size_before = os.path.getsize(db.path)

    # Act
    with pytest.raises(ValueError):
        db.set("a,b", "value")

    # Assert
    assert os.path.getsize(db.path) == size_before

"""Regression tests for issue #21: set and delete confirm what they did."""

import pytest
from pykv import Database


@pytest.fixture
def db(tmp_path):
    """Each test gets its own database in a temporary file."""
    return Database(tmp_path / "test_data.txt")


def test_set_returns_true_when_the_value_is_stored(db):
    """Issue #21: set confirms that the record was written."""
    # Act
    result = db.set("greeting", "Hello")

    # Assert
    assert result is True
    assert db.get("greeting") == "Hello"


def test_delete_returns_true_when_the_key_existed(db):
    """Issue #21: delete confirms that a live key was removed."""
    # Arrange
    db.set("temp", "data")

    # Act
    result = db.delete("temp")

    # Assert
    assert result is True
    assert db.get("temp") is None


def test_delete_returns_false_when_the_key_does_not_exist(db):
    """Issue #21: delete tells the caller that there was nothing to remove."""
    # Act
    result = db.delete("ghost")

    # Assert
    assert result is False


def test_delete_twice_returns_false_the_second_time(db):
    """Issue #21: a key that is already deleted is reported as not found."""
    # Arrange
    db.set("temp", "data")
    db.delete("temp")

    # Act
    result = db.delete("temp")

    # Assert
    assert result is False

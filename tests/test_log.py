import pytest
from pykv.log import TOMBSTONE, Log


@pytest.fixture
def log(tmp_path):
    """Each test gets its own log in a temporary file."""
    return Log(tmp_path / "test_log.txt")


def test_append_returns_where_the_record_starts(log):
    """Check that positions count bytes, also with multibyte characters."""
    # Arrange
    log.append("ñ", "ñ")  # 6 bytes in UTF-8

    # Act
    offset = log.append("b", "2")

    # Assert
    assert offset == 6


def test_read_returns_the_value_at_that_position(log):
    """Check that read gets the value of the record at the given position."""
    # Arrange
    log.append("a", "1")
    offset = log.append("b", " Привет ")

    # Act
    value = log.read(offset)

    # Assert
    assert value == " Привет "


def test_records_are_read_in_order_with_tombstones_as_none(log):
    """Check that records returns every operation, and None for a deletion."""
    # Arrange
    first = log.append("a", "1")
    log.append_tombstone("a")

    # Act
    records = list(log.records())

    # Assert
    assert records[0] == (first, "a", "1")
    assert records[1][1:] == ("a", None)


def test_tombstone_is_the_only_value_read_as_none(log):
    """Check that a value that only looks similar to the marker is kept."""
    # Arrange
    log.append("a", TOMBSTONE + "x")

    # Act
    _, _, value = next(log.records())

    # Assert
    assert value == TOMBSTONE + "x"


def test_records_creates_the_file_if_it_does_not_exist(log):
    """Check that reading a log that does not exist leaves it created and empty."""
    # Arrange: the fixture does not create the file

    # Act
    records = list(log.records())

    # Assert
    assert records == []
    with open(log.path, "rb") as f:
        assert f.read() == b""

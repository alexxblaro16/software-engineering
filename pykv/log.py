import os

# Value written to the log to mark a deleted key
TOMBSTONE = "__DELETED__"


class Log:
    """Append-only log file. Only this class knows how records are stored.

    Everything about the file lives here, so that splitting the log into
    segments in phase 2 only changes this class.
    """

    def __init__(self, path):
        self.path = str(path)

    def _append_line(self, key, value):
        """Writes one record at the end of the file and returns where it starts."""
        with open(self.path, "ab") as f:
            offset = f.tell()  # Byte position at the end of the file
            f.write(f"{key},{value}\n".encode("utf-8"))
        return offset

    def append(self, key, value):
        """Appends a key and its value, and returns the position of the record."""
        return self._append_line(key, value)

    def append_tombstone(self, key):
        """Appends a record that marks the key as deleted."""
        self._append_line(key, TOMBSTONE)

    def read(self, offset):
        """Returns the value of the record that starts at this position."""
        with open(self.path, "rb") as f:
            f.seek(offset)  # Jump directly to the exact byte position
            line = f.readline().decode("utf-8")
        _, value = line.rstrip("\r\n").split(",", 1)
        return value

    def records(self):
        """Yields (offset, key, value) from start to end; value is None if deleted."""
        if not os.path.exists(self.path):
            # First start: create an empty log file so the database is ready
            open(self.path, "w", encoding="utf-8").close()
            return

        offset = 0  # Byte position where the current line starts
        with open(self.path, "rb") as f:
            for raw_line in f:
                line_offset = offset
                offset += len(raw_line)  # The next line starts after this one

                parts = raw_line.decode("utf-8").rstrip("\r\n").split(",", 1)
                if len(parts) == 2:
                    key, value = parts
                    yield line_offset, key, None if value == TOMBSTONE else value

from pykv.log import TOMBSTONE, Log


class Database:
    """Key-value database stored in an append-only log file."""

    def __init__(self, path="db.txt"):
        self.path = str(path)
        self.log = Log(self.path)
        # Hash map / Index in memory: stores { "key": byte_offset }
        self.index = {}
        self.build_index()

    def _check_key(self, key):
        """Raises a clear error if the key cannot be stored in the log."""
        if not isinstance(key, str):
            raise TypeError("The key must be a string")
        if key == "":
            raise ValueError("The key cannot be empty")
        if "," in key or "\n" in key or "\r" in key:
            raise ValueError("The key cannot contain commas or line breaks")

    def _check_value(self, value):
        """Raises a clear error if the value cannot be stored in the log."""
        if not isinstance(value, str):
            raise TypeError("The value must be a string")
        if "\n" in value or "\r" in value:
            raise ValueError("The value cannot contain line breaks")
        if value == TOMBSTONE:
            raise ValueError(f"{TOMBSTONE} is reserved to mark deleted keys")

    def build_index(self):
        """Reads the log once on startup to build the hash map index."""
        self.index.clear()
        for offset, key, value in self.log.records():
            if value is None:
                self.index.pop(key, None)  # Tombstone: remove from index
            else:
                self.index[key] = offset  # Save the latest position

    def set(self, key, value):
        """Appends data to the log and updates the hash map."""
        self._check_key(key)
        self._check_value(value)
        self.index[key] = self.log.append(key, value)

    def get(self, key):
        """Retrieves data using the hash map (no full file scan)."""
        self._check_key(key)
        if key not in self.index:
            return None
        return self.log.read(self.index[key])

    def delete(self, key):
        """Deletes by writing a tombstone and removing it from the hash map."""
        self._check_key(key)
        if key in self.index:
            self.log.append_tombstone(key)
            del self.index[key]

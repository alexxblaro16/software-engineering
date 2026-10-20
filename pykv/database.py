import os


class Database:
    """Key-value database stored in an append-only log file."""

    def __init__(self, path="db.txt"):
        self.path = str(path)
        # Hash map / Index in memory: stores { "key": byte_offset }
        self.index = {}
        self.build_index()

    def build_index(self):
        """Reads the file once on startup to build the hash map index."""
        self.index.clear()
        if not os.path.exists(self.path):
            # First start: create an empty log file so the database is ready
            open(self.path, "w", encoding="utf-8").close()
            return

        offset = 0  # Byte position where the current line starts
        with open(self.path, "rb") as f:
            for raw_line in f:
                line_offset = offset
                offset += len(raw_line)  # The next line starts after this one

                parts = raw_line.decode("utf-8").strip().split(",", 1)
                if len(parts) == 2:
                    key, value = parts
                    if value == "__DELETED__":
                        self.index.pop(key, None)  # Tombstone: remove from index
                    else:
                        self.index[key] = line_offset  # Save the latest position

    def set(self, key, value):
        """Appends data to the file and updates the hash map."""
        with open(self.path, "ab") as f:
            offset = f.tell()  # Byte position at the end of the file
            f.write(f"{key},{value}\n".encode("utf-8"))

        self.index[key] = offset  # Update hash map

    def get(self, key):
        """Retrieves data using the hash map and seek() (no full file scan)."""
        if key not in self.index:
            return None

        offset = self.index[key]
        with open(self.path, "rb") as f:
            f.seek(offset)  # Jump directly to the exact byte position
            line = f.readline().decode("utf-8")
            _, value = line.strip().split(",", 1)
            return value

    def delete(self, key):
        """Deletes by writing a tombstone and removing it from the hash map."""
        if key in self.index:
            with open(self.path, "ab") as f:
                f.write(f"{key},__DELETED__\n".encode("utf-8"))
            del self.index[key]


# --- TEST BLOCK ---
if __name__ == "__main__":
    db = Database()

    # 1. Test team
    db.set("team", "Alejandro, Gabriel, Jorge")
    print("Get team:", db.get("team"))

    # 2. Add student
    db.set("student", "Miguel")
    print("Get student (added):", db.get("student"))

    # 3. Delete student using tombstone
    db.delete("student")
    print("Get student (after delete):", db.get("student"))

    # 4. Check final team
    print("Get final team:", db.get("team"))

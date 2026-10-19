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
            return

        with open(self.path, "r", encoding="utf-8") as f:
            while True:
                offset = f.tell()  # Save byte position before reading the line
                line = f.readline()
                if not line:
                    break

                parts = line.strip().split(",", 1)
                if len(parts) == 2:
                    key, value = parts
                    if value == "__DELETED__":
                        self.index.pop(key, None)  # Tombstone: remove from index
                    else:
                        self.index[key] = offset  # Save the latest position

    def set(self, key, value):
        """Appends data to the file and updates the hash map."""
        with open(self.path, "a", encoding="utf-8") as f:
            offset = f.tell()  # Get current byte position
            f.write(f"{key},{value}\n")

        self.index[key] = offset  # Update hash map

    def get(self, key):
        """Retrieves data using the hash map and seek() (no full file scan)."""
        if key not in self.index:
            return None

        offset = self.index[key]
        with open(self.path, "r", encoding="utf-8") as f:
            f.seek(offset)  # Jump directly to the exact byte position
            _, value = f.readline().strip().split(",", 1)
            return value

    def delete(self, key):
        """Deletes by writing a tombstone and removing it from the hash map."""
        if key in self.index:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(f"{key},__DELETED__\n")
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

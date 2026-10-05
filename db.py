import os

DB_FILE = "db.txt"
# Hash map / Index in memory: stores { "key": byte_offset }
INDEX = {}

def build_index():
    """Reads the file once on startup to build the hash map index."""
    if not os.path.exists(DB_FILE):
        return
    
    with open(DB_FILE, "r", encoding="utf-8") as f:
        while True:
            offset = f.tell()  # Save byte position before reading the line
            line = f.readline()
            if not line:
                break
            
            parts = line.strip().split(",", 1)
            if len(parts) == 2:
                key, value = parts
                if value == "__DELETED__":
                    INDEX.pop(key, None)  # Tombstone: remove from index
                else:
                    INDEX[key] = offset  # Save the latest position


def set(key, value):
    """Appends data to the file and updates the hash map."""
    with open(DB_FILE, "a", encoding="utf-8") as f:
        offset = f.tell()  # Get current byte position
        f.write(f"{key},{value}\n")
    
    INDEX[key] = offset  # Update hash map


def get(key):
    """Retrieves data instantly using the hash map and seek() (no full file scan)."""
    if key not in INDEX:
        return None
    
    offset = INDEX[key]
    with open(DB_FILE, "r", encoding="utf-8") as f:
        f.seek(offset)  # Jump directly to the exact byte position
        _, value = f.readline().strip().split(",", 1)
        return value


def delete(key):
    """Deletes by writing a tombstone and removing it from the hash map."""
    if key in INDEX:
        with open(DB_FILE, "a", encoding="utf-8") as f:
            f.write(f"{key},__DELETED__\n")
        del INDEX[key]


# --- TEST WITH MIGUEL ---
if __name__ == "__main__":
    build_index()  # Build index on startup
    
    # 1. Test team
    set("team", "Alejandro, Gabriel, Jorge")
    print("Get team:", get("team"))
    
    # 2. Add Miguel
    set("student", "Miguel")
    print("Get student (added):", get("student"))
    
    # 3. Delete Miguel using tombstone
    delete("student")
    print("Get student (after delete):", get("student"))
    
    # 4. Check final team
    print("Get final team:", get("team"))
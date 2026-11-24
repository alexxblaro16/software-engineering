"""Session 8 experiment: how much the log grows with a single key.

Writes 1,000,000 values to the same key and measures the size of the log
file and the time it takes to rebuild the index when the database is opened.

Run it from the root of the repository:

    python experiments/log_growth.py
"""

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pykv import Database  # noqa: E402

WRITES = 1_000_000
KEY = "language"


def main():
    with tempfile.TemporaryDirectory() as folder:
        log_path = Path(folder) / "experiment.log"
        db = Database(log_path)

        start = time.perf_counter()
        for i in range(WRITES):
            db.set(KEY, f"value-{i}")
        write_time = time.perf_counter() - start

        size = os.path.getsize(log_path)

        start = time.perf_counter()
        db.build_index()
        rebuild_time = time.perf_counter() - start

        print(f"Writes to '{KEY}':     {WRITES:,}")
        print(f"Keys in the index:     {len(db.index)}")
        print(f"Last value:            {db.get(KEY)}")
        print(f"Log file size:         {size:,} bytes ({size / 1e6:.1f} MB)")
        print(f"Time to write:         {write_time:.1f} s")
        print(f"Time to rebuild index: {rebuild_time:.3f} s")


if __name__ == "__main__":
    main()

# PyKV: Python Key-Value Database Engine

An ultralightweight key-value database engine written in pure Python, built for programmers who need a simple, reliable and auditable way to read, write and modify data.

PyKV is developed as the Software Engineering course project at **UDIT**.

---

## Description

PyKV stores data using three simple ideas:

- **Append-only log:** every operation (`set` and `delete`) is appended to the end of a single data file. Existing records are never overwritten, so the file is a complete, ordered history of everything that happened to the data.
- **In-memory hash index:** a hash map (a Python `dict`) keeps, for every key, the byte position of its most recent record in the log file.
- **`f.seek()` byte jumps:** to read a value, the engine looks up the key in the hash index and jumps directly to the stored byte offset with `f.seek()`. It never scans the whole file, so read time does not grow with the size of the log.

Deletions are recorded as **tombstones**: special records appended to the log that mark a key as removed while keeping the previous history intact. When the database is opened, the index is rebuilt by reading the log from start to end, so the latest record of each key (or its tombstone) determines its current state.

```
   set("a", 1)   set("b", 2)   set("a", 3)   delete("b")
        │             │             │             │
        ▼             ▼             ▼             ▼
  ┌───────────┬───────────┬───────────┬───────────┐
  │  a = 1    │  b = 2    │  a = 3    │ b (tomb.) │   append-only log
  └───────────┴───────────┴───────────┴───────────┘
        Hash index (in memory):   a → offset of "a = 3"
                                  b → removed
```

---

## Authors / Team

| Name |
|------|
| Alejandro Blanco Rodríguez |
| Gabriel Calvo Ballesteros |
| Jorge Tort Soler |

Software Engineering course, UDIT.

---

## Key Features

- **Simple key-value operations:** `set`, `get` and `delete`, designed for a fast and intuitive workflow for Python developers.
- **Optimized performance:** operations are designed to respond in **under 500 ms**, thanks to the in-memory hash index and direct access to data with `f.seek()`, even with large amounts of data.
- **Constant auditing through the log:** the append-only log keeps the full history of insertions, modifications and deletions (via tombstones), so the workflow can always be traced and reviewed.
- **Crash recovery:** the index is rebuilt from the log every time the database is opened, without manual intervention.
- **Robust text encoding:** data is stored using explicit UTF-8 encoding so that international text (for example, Cyrillic) is saved and retrieved correctly on any operating system.
- **Portable and lightweight:** pure Python with no runtime dependencies, designed to run on multiple operating systems and on older machines.

---

## Prerequisites & Environment Setup

### Prerequisites

- [Python 3.12](https://www.python.org/downloads/) or newer (the CI runs on 3.12)
- [Git](https://git-scm.com/downloads)

### 1. Clone the repository

```bash
git clone https://github.com/alexxblaro16/software-engineering.git
cd software-engineering
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

On some systems the command is `python3` instead of `python`.

### 3. Activate the virtual environment

**Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

When the environment is active, your terminal prompt shows `(venv)` at the beginning.

### 4. Install dependencies

The project uses the following development tools:

| Tool | Purpose |
|------|---------|
| `pytest` | Automated testing |
| `black` | Code formatting |
| `flake8` | Linting and style checks |

Install them with:

```bash
pip install -r requirements.txt
```

To leave the virtual environment, run `deactivate`.

---

## Usage Example

```python
from pykv import Database

db = Database("data.log")

db.set("greeting", "Hello")
print(db.get("greeting"))   # Hello

db.set("greeting", "Привет")  # modification: a new record is appended
print(db.get("greeting"))   # Привет

db.delete("greeting")       # a tombstone is appended to the log
print(db.get("greeting"))   # None (key no longer available)
```

---

## Running Tests

With the virtual environment active, run the whole test suite from the root of the repository:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

To run a single test file:

```bash
pytest tests/test_db.py
```

If everything is working correctly, pytest finishes with all tests marked as passed (green). Any failure is reported with the test name and the line where it occurred.

### Code quality checks

```bash
black .          # format the code
flake8           # check style and common errors
```

---

## Repository Structure

```
.
├── pykv/            # PyKV module
│   ├── __init__.py
│   └── database.py  # Database class: append-only log, in-memory hash index, set/get/delete
├── tests/           # Automated tests (pytest)
│   └── test_db.py
├── BACKLOG.md       # Product backlog: user stories and acceptance criteria
├── requirements.txt # Development dependencies (pytest, black, flake8)
├── .github/         # CI workflow (GitHub Actions) and CODEOWNERS
├── .gitignore       # Files ignored by Git (e.g. venv/, __pycache__/, data files)
└── README.md        # Project documentation (this file)
```


---

## Contributing

Nobody pushes directly to `main`. Every change follows the same steps:

1. Create a branch for the task, named after the commit type (`feat/...`, `fix/...`, `docs/...`, `test/...`).
2. Commit using Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `ci:`).
3. Push the branch and open a Pull Request. GitHub Actions runs flake8 and pytest on it.
4. Another team member reviews it. Once the CI is green and it is approved, it is merged and the branch is deleted.

---

## Documentation

The product backlog, with the user stories and acceptance criteria that drive the development of the project, is available in [BACKLOG.md](BACKLOG.md).

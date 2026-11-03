# PRODUCT BACKLOG

**Project:** Ultralightweight key-value database in Python
**Course:** Software Engineering — UDIT
**Methodology:** Scrum / Agile (User Stories following the INVEST criteria)
**Document version:** 1.0.

---

## 1. Product Vision

A **minimal and reliable** key-value database written in Python, designed by and for programmers. It offers `set`, `get` and `delete` operations on an **append-only log** on disk, with an **in-memory hash index** that stores the position of each key in the file and allows it to be retrieved with `f.seek()` without scanning the log.

## 2. Client Requirements and Traceability

| ID | Client requirement | Related stories |
|----|--------------------|-----------------|
| R1 | Volume and performance: large amounts of data, responses guaranteed in under 500 ms | US-01, US-02 |
| R2 | Availability and security: highly important data, 24/7 operation (including night shifts) and high reliability against failures | US-03, US-04 |
| R3 | Traceability: workflow auditing through a historical log, with modifications and deletions handled as tombstones | US-05 |
| R4 | User profile: Python programmers, agile workflow to read/write/modify data with the simplest possible key-value database | US-06 |
| R5 | Compatibility: multiple operating systems, older machines and international clients (e.g. Russia) with robust encoding | US-07 |

## 3. Assumptions to Validate with the Client

The requirements use qualitative terms ("massive", "extremely important"). To make them testable, the following measurable values are proposed and must be confirmed with the client:

- **Reference volume:** 1,000,000 keys and a log file of several hundred MB.
- **Latency:** the 500 ms limit is taken as the maximum for the **99th percentile (p99)** of each operation.
- **Security:** interpreted as **integrity and reliability against failures** (no data loss or corruption). Encryption and access control are **not** part of the requirements and are out of scope for this backlog.
- **Reference old machine:** for example, 2 cores, 4 GB of RAM and an HDD (to be confirmed).
- **Supported Python versions:** to be fixed in Sprint 0 (to be confirmed).

---

## 4. Definition of Done (DoD)

A task or story is done when we can answer "yes" to all of these questions:

1. Has it been merged into `main` through a Pull Request?
2. Is the CI (flake8 + pytest) green on that Pull Request?
3. Does the new code have its own tests, following Arrange, Act, Assert?
4. Has another team member reviewed and approved it?
5. Do the branch name and the commits follow Conventional Commits (`feat`, `fix`, `test`, `docs`...)?
6. If it changes how PyKV is used, has the README been updated?

The Definition of Done is the same for every task. The acceptance criteria in section 6 are different: each one belongs to a single story and checks what the client asked for.

---

## 5. Backlog Summary

| ID | Story | Requirement | Priority (MoSCoW) | Points | Suggested sprint |
|----|-------|-------------|-------------------|--------|------------------|
| US-06 | Simple API for Python programmers | R4 | Must | 3 | 1 |
| US-05 | Append-only historical log and tombstones | R3 | Must | 5 | 1 |
| US-02 | In-memory hash index for large volumes | R1 | Must | 5 | 2 |
| US-03 | 24/7 continuous operation and recovery after restart | R2 | Must | 5 | 2 |
| US-01 | Response in under 500 ms | R1 | Should | 5 | 1 |
| US-07 | Multi-platform, older machines and UTF-8 encoding | R5 | Should | 5 | 3 |
| US-04 | Reliability against failures and integrity protection | R2 | Won't (this time) | 8 | - |

**MoSCoW check:** Must stories (US-06, US-05, US-02 and US-03) add up to 18 of 36 points (50%), below the 60% limit. US-04 is Won't for this delivery; US-01 and US-07 are Should. The points come from the Planning Poker in section 5.1.


### 5.1 Planning Poker

Each team member voted the story points on their own with the Fibonacci scale (1, 2, 3, 5, 8, 13). Where the votes did not match, the agreed value is the one chosen by two of the three members.

| ID | Alejandro | Gabriel | Jorge | Agreed | Justification |
|----|-----------|---------|-------|--------|---------------|
| US-06 | 3 | 3 | 3 | 3 | Simple Python API with basic CRUD operations |
| US-05 | 5 | 5 | 5 | 5 | Persistent log and logical deletion |
| US-02 | 5 | 5 | 5 | 5 | In-memory index for efficient access |
| US-03 | 5 | 5 | 5 | 5 | Recovery after restarting the database |
| US-01 | 5 | 8 | 5 | 5 | Performance testing and optimization. Gabriel saw more risk in measuring 500 ms on older machines |
| US-07 | 5 | 5 | 5 | 5 | Compatibility across platforms and UTF-8 |
| US-04 | 8 | 13 | 8 | 8 | Complex failure handling and data integrity. Gabriel saw more risk in records cut by a crash |

US-01 stays as Should: as a Must it would take the Must total to 23 of 36 points (63.9%), above the 60% limit.

## 6. User Stories

### US-01 — Response in under 500 ms

**Requirement:** R1 (Volume and performance)

> **As a** programmer integrating the database into an application,
> **I want** the `get`, `set` and `delete` operations to respond in under 500 ms even with a large volume of data,
> **so that** my application delivers instant responses to its users.

**Acceptance criteria**

- **AC-01.1 — Fast read under heavy load**
  - **Given** a database with 1,000,000 keys,
  - **when** `get(key)` is executed on an existing key,
  - **then** the response arrives in under 500 ms (p99 measured over at least 1,000 reads).
- **AC-01.2 — Fast write under heavy load**
  - **Given** a database with 1,000,000 keys,
  - **when** `set(key, value)` is executed,
  - **then** the operation is confirmed in under 500 ms (p99 measured over at least 1,000 writes).
- **AC-01.3 — Non-existent key**
  - **Given** a key that does not exist,
  - **when** `get(key)` is executed,
  - **then** the "not found" result is also returned in under 500 ms.
- **AC-01.4 — Automated test**
  - **Given** the performance test suite,
  - **when** it runs in the continuous integration environment,
  - **then** it fails if any p99 exceeds 500 ms.

**INVEST analysis**

| Criterion | Compliance |
|-----------|------------|
| Independent | Depends only on having a `set/get` core; can be tested in isolation. |
| Negotiable | The volume threshold and the percentile are negotiable with the client. |
| Valuable | It is an explicit client requirement (instant response). |
| Estimable | It is a performance test with a clear threshold (5 points). |
| Small | Fits in one sprint. |
| Testable | Verifiable with automated timing. |

---

### US-02 — In-memory Hash Index for Large Volumes

**Requirement:** R1 (Volume and performance)

> **As a** programmer storing a massive amount of data,
> **I want** the database to keep an in-memory hash map with the position of each key in the file,
> **so that** I can read any value with a single `f.seek()` without scanning the whole log.

**Acceptance criteria**

- **AC-02.1 — Direct access by position**
  - **Given** a log with 1,000,000 records,
  - **when** `get(key)` is executed,
  - **then** the system queries the hash map, obtains the offset and reads the value with `f.seek()` without scanning the file.
- **AC-02.2 — Index updated on write**
  - **Given** an existing key,
  - **when** `set(key, new_value)` is executed,
  - **then** the index points to the new record and `get(key)` returns the most recent value.
- **AC-02.3 — Read cost independent of size**
  - **Given** two databases, one with 10,000 and another with 1,000,000 keys,
  - **when** `get(key)` is measured on both,
  - **then** the time does not grow proportionally to the number of records.
- **AC-02.4 — Index rebuild**
  - **Given** an existing log file,
  - **when** the database is opened,
  - **then** the hash map is rebuilt by reading the log and reflects the latest value of each key.

**INVEST analysis**

| Criterion | Compliance |
|-----------|------------|
| Independent | Built on the log format defined in US-05, without depending on the rest. |
| Negotiable | The index structure (`dict`) and its contents can be adjusted. |
| Valuable | It is the reason reads are fast with massive data. |
| Estimable | Well-known design: `dict` from key to offset (5 points). |
| Small | Fits in one sprint. |
| Testable | Checked with correctness and scaling tests. |

---

### US-03 — 24/7 Continuous Operation and Recovery After Restart

**Requirement:** R2 (Availability and security)

> **As an** operations manager of a system that runs 24/7, including night shifts,
> **I want** the database to run continuously and recover on its own after a restart or crash,
> **so that** I do not depend on manual intervention and the service is not interrupted overnight.

**Acceptance criteria**

- **AC-03.1 — Prolonged operation**
  - **Given** the database running with continuous operations,
  - **when** at least 24 hours of stability testing elapse,
  - **then** there are no crashes and no sustained increase in memory usage (no leaks).
- **AC-03.2 — Automatic recovery**
  - **Given** that the process is interrupted and launched again,
  - **when** the database is opened,
  - **then** the index is rebuilt from the log without manual intervention and the previous data remains available.
- **AC-03.3 — Bounded startup time**
  - **Given** a log with 1,000,000 records,
  - **when** the service is restarted,
  - **then** the recovery time is measured, documented and within the target agreed with the client.
- **AC-03.4 — Controlled errors**
  - **Given** an I/O error (for example, a full disk),
  - **when** it occurs during an operation,
  - **then** the system reports a clear exception and does not end up in an inconsistent state.

**INVEST analysis**

| Criterion | Compliance |
|-----------|------------|
| Independent | Relies on the log from US-05, but can be developed in parallel with a clear contract. |
| Negotiable | The startup time and the duration of the test are negotiable. |
| Valuable | Addresses the 24/7 continuous operation requirement. |
| Estimable | Bounded scope (5 points). |
| Small | Fits in one sprint. |
| Testable | Stability test and restart simulation. |

---

### US-04 — Reliability Against Failures and Integrity Protection

**Requirement:** R2 (Availability and security)

> **As a** person responsible for extremely important data,
> **I want** a power outage or process failure to never corrupt or lose already confirmed data,
> **so that** I can trust that the stored information is intact and reliable.

**Acceptance criteria**

- **AC-04.1 — Confirmed write is persisted write**
  - **Given** that `set` returns a confirmation,
  - **when** the process is interrupted immediately afterwards,
  - **then** the data is on disk and is recovered on restart.
- **AC-04.2 — Incomplete final record**
  - **Given** that the process was cut off mid-write and the last record was left truncated,
  - **when** the database is opened,
  - **then** the incomplete record is detected and ignored, and all previous records remain intact.
- **AC-04.3 — Corruption detection**
  - **Given** a record whose content was altered,
  - **when** it is read or the index is rebuilt,
  - **then** it is detected through an integrity check (for example, a checksum per record) and the error is reported without returning false data.
- **AC-04.4 — No modification of what is already written**
  - **Given** an already written record,
  - **when** subsequent operations are performed,
  - **then** the file only grows at the end and earlier data is not overwritten.
- **AC-04.5 — Failure testing**
  - **Given** a set of tests that simulate interruptions at different points of the write,
  - **when** they are executed,
  - **then** none produces loss of confirmed data or corruption.

**INVEST analysis**

| Criterion | Compliance |
|-----------|------------|
| Independent | Based on the log format, with criteria that can be verified separately. |
| Negotiable | The mechanism (checksum, disk-sync policy) is decided during the sprint. |
| Valuable | Covers "high security/reliability against failures" for critical data. |
| Estimable | Medium technical uncertainty; estimated at 8 points. |
| Small | Can be split in two if the team sees fit (persistence / corruption detection). |
| Testable | Verifiable with fault injection and truncation tests. |

---

### US-05 — Append-only Historical Log with Tombstones

**Requirement:** R3 (Traceability)

> **As a** workflow auditor,
> **I want** every insertion, modification and deletion to be recorded in a write-at-the-end-only historical log, with deletions marked as tombstones,
> **so that** I can reconstruct and review at any time what happened to each piece of data.

**Acceptance criteria**

- **AC-05.1 — Insertion recorded**
  - **Given** a new key,
  - **when** `set(key, value)` is executed,
  - **then** a record is appended to the end of the log with the key, the value and the order of the operation.
- **AC-05.2 — Modification preserves history**
  - **Given** an existing key,
  - **when** `set(key, other_value)` is executed,
  - **then** a new record is appended without deleting the previous one, and `get` returns the most recent one.
- **AC-05.3 — Deletion through a tombstone**
  - **Given** an existing key,
  - **when** `delete(key)` is executed,
  - **then** a tombstone-type record is appended to the log, the key is no longer available in `get`, and the previous history remains in the file.
- **AC-05.4 — Rebuild respecting tombstones**
  - **Given** a log with insertions, modifications and deletions,
  - **when** the index is rebuilt on opening the database,
  - **then** keys whose last record is a tombstone do not appear in the index.
- **AC-05.5 — Auditable order**
  - **Given** the log file,
  - **when** it is read from start to end,
  - **then** operations appear in the exact order in which they were performed.

**INVEST analysis**

| Criterion | Compliance |
|-----------|------------|
| Independent | It is the foundation of the data format; it does not depend on other stories. |
| Negotiable | The record format is negotiable within the client's constraints. |
| Valuable | Directly covers the constant auditing requirement. |
| Estimable | Clear design: insertion, modification and tombstone (5 points). |
| Small | Fits in one sprint. |
| Testable | Verified by inspecting the log after sequences of operations. |

---

### US-06 — Simple API for Python Programmers

**Requirement:** R4 (User profile and technologies)

> **As a** Python programmer,
> **I want** to read, write and modify data with a minimal and intuitive API (`set`, `get`, `delete`),
> **so that** I can integrate the database into my project in a few minutes without learning a complex system.

**Acceptance criteria**

- **AC-06.1 — Basic usage in a few lines**
  - **Given** a Python project with the library installed,
  - **when** `db.set("key", "value")` and `db.get("key")` are written,
  - **then** the value is stored and retrieved correctly with no additional configuration.
- **AC-06.2 — Modification and deletion**
  - **Given** an existing key,
  - **when** `set` is used with a new value, or `delete`,
  - **then** the change is immediately reflected in subsequent reads.
- **AC-06.3 — No external dependencies**
  - **Given** a clean Python environment,
  - **when** the library is installed and used,
  - **then** it works using only the Python standard library.
- **AC-06.4 — Documentation with an example**
  - **Given** the repository README,
  - **when** a programmer reads it,
  - **then** they find a complete usage example that they can run right away.
- **AC-06.5 — Understandable errors**
  - **Given** incorrect usage (for example, an unsupported key type),
  - **when** the operation is executed,
  - **then** an exception with a clear message is raised.

**INVEST analysis**

| Criterion | Compliance |
|-----------|------------|
| Independent | It is the public layer over the core; it can be developed with a provisional implementation. |
| Negotiable | Method names and signatures can be adjusted. |
| Valuable | Meets the requirement of the simplest possible key-value database for programmers. |
| Estimable | Small, well-known API (3 points). |
| Small | Fits in one sprint. |
| Testable | Validated with unit tests and with the README example. |

---

### US-07 — Multi-platform, Older Machines and Robust Encoding

**Requirement:** R5 (Compatibility and environment)

> **As a** deployment manager working with international clients (for example, in Russia),
> **I want** the database to work on different operating systems and on older machines, and to store and retrieve text in any language without errors,
> **so that** I can install it in each client's environment and neither lose nor distort their data.

**Acceptance criteria**

- **AC-07.1 — Several operating systems**
  - **Given** the automated tests,
  - **when** they run on Windows, Linux and macOS,
  - **then** all of them pass with no code changes.
- **AC-07.2 — Supported Python versions**
  - **Given** the Python versions defined as supported (including the oldest ones agreed with the client),
  - **when** the test suite runs on each of them,
  - **then** all of them pass.
- **AC-07.3 — Limited resources**
  - **Given** a reference old machine (for example, 2 cores and 4 GB of RAM),
  - **when** the performance tests from US-01 are executed,
  - **then** the 500 ms limit is met or the maximum volume supported on that machine is documented.
- **AC-07.4 — Explicit UTF-8 encoding**
  - **Given** that the file is always opened with explicit UTF-8 encoding, independent of the system's regional settings,
  - **when** the value `"Привет, мир"` (Cyrillic) is stored with the key `"cliente_Москва"`,
  - **then** `get` returns exactly the same text on Windows, Linux and macOS.
- **AC-07.5 — Correct offsets with multibyte characters**
  - **Given** values with multibyte characters (Cyrillic, accents, emojis),
  - **when** they are read using `f.seek()`,
  - **then** the offsets are calculated in **bytes** (not characters) and the value is retrieved without being truncated or corrupted.
- **AC-07.6 — Consistent line endings**
  - **Given** that the same log file is created on one operating system and opened on another,
  - **when** the index is rebuilt,
  - **then** the data is read correctly with no differences caused by the line-ending format.

**INVEST analysis**

| Criterion | Compliance |
|-----------|------------|
| Independent | Validated as a cross-cutting set of tests, without depending on a specific feature. |
| Negotiable | The list of operating systems and Python versions is agreed with the client. |
| Valuable | Covers the compatibility and internationalization requirement. |
| Estimable | Defined scope of 5 points. |
| Small | Fits in one sprint. |
| Testable | Verified with multi-OS continuous integration and Cyrillic data. |

---

## 7. Proposed Work Order

| Sprint | Stories | Goal |
|--------|---------|------|
| Sprint 0 | — | Repository, project structure, testing tools, CI, and decisions on Python versions and operating systems |
| Sprint 1 | US-06, US-05, US-01 | Functional core: API, append-only log with tombstones and first performance measurement |
| Sprint 2 | US-02, US-03 | Hash index with `f.seek()`, rebuild and continuous recovery |
| Sprint 3 | US-07 | Multi-platform compatibility with UTF-8 (US-04 is Won't for this delivery) |

## 8. Identified Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| The log grows indefinitely due to its append-only nature | Higher disk usage and slower startups | Register log compaction as a future story, provided it does not go against the client's audit requirement (R3) |
| The whole index must fit in memory | Limit on older machines | Document the maximum supported volume (AC-07.3) |
| Guaranteeing persistence may affect latency | Risk to the 500 ms target | Measure both objectives together in the US-01 and US-04 tests |
| Poorly defined qualitative requirements | Rework | Validate the assumptions in section 3 in the first review with the client |

---

## 9. System Requirements for the Must Stories

The user stories in section 6 say what the client needs. These requirements say exactly what the system does, so that whoever programs or tests it does not have to fill in the gaps. Each one answers one of three questions (inputs and outputs, errors, limits) and can be checked with a yes or a no.

The tests in the last column are in `tests/`. `test_sr_*` tests are in `tests/test_system_requirements.py`.

### US-06 — Simple API for Python Programmers

| ID | Type | Requirement | Checked by |
|----|------|-------------|------------|
| SR-06.1 | Inputs and outputs | `set(key, value)` stores a string under a string key, and `get(key)` returns the last value stored for that key. | `test_set_and_get`, `test_update_value` |
| SR-06.2 | Inputs and outputs | `get` on a key that does not exist returns `None`. `delete` on a key that does not exist raises nothing and writes nothing. | `test_non_existent_key`, `test_sr_06_2_delete_of_unknown_key_writes_nothing` |
| SR-06.3 | Errors | A key that is not a string raises `TypeError`. An empty key, or one with a comma or a line break, raises `ValueError`. `set`, `get` and `delete` all apply this, and nothing is written to the log. | `tests/test_validation.py` |
| SR-06.4 | Errors | In `set`, a value that is not a string raises `TypeError`, and a value with a line break raises `ValueError`. | `test_value_that_is_not_a_string_is_rejected`, `test_value_with_line_break_is_rejected` (PR #16) |
| SR-06.5 | Limits | The code in `pykv/` imports only the Python standard library. | `test_sr_06_5_runtime_code_only_uses_the_standard_library` |

### US-05 — Append-only Historical Log with Tombstones

| ID | Type | Requirement | Checked by |
|----|------|-------------|------------|
| SR-05.1 | Inputs and outputs | Each `set` appends exactly one line, `key,value\n`, encoded in UTF-8, to the end of the log. | `test_sr_05_1_set_appends_one_utf8_line` |
| SR-05.2 | Inputs and outputs | `set` on an existing key leaves every byte already in the log unchanged. | `test_sr_05_2_update_keeps_the_previous_bytes` |
| SR-05.3 | Inputs and outputs | `delete` on an existing key appends the line `key,__DELETED__\n` and leaves every byte already in the log unchanged. | `test_sr_05_3_delete_appends_a_tombstone` |
| SR-05.4 | Inputs and outputs | Read from start to end, the log shows the operations in the order in which they were performed. | `test_sr_05_4_log_keeps_the_order_of_the_operations` |
| SR-05.5 | Errors | `set` with the value `__DELETED__` raises `ValueError`, because that value is reserved for tombstones. | `test_tombstone_value_is_rejected` (PR #16) |

### US-02 — In-memory Hash Index for Large Volumes

| ID | Type | Requirement | Checked by |
|----|------|-------------|------------|
| SR-02.1 | Inputs and outputs | For each live key, the index stores the position in bytes (not characters) where its latest record starts. | `test_sr_02_1_index_stores_the_byte_offset_of_the_last_record` |
| SR-02.2 | Inputs and outputs | `get` jumps with `f.seek()` to the position in the index and reads only that record. | `test_sr_02_2_get_reads_only_the_record_of_the_key` |
| SR-02.3 | Inputs and outputs | After `delete`, the key is no longer in the index. | `test_sr_02_3_delete_removes_the_key_from_the_index` |
| SR-02.4 | Inputs and outputs | Values with multibyte characters are returned complete. | `test_byte_offsets_multibyte`, `test_utf8_encoding_and_cyrillic` |
| SR-02.5 | Limits | With 1,000,000 keys, the 99th percentile of `get`, measured over 1,000 reads, is under 500 ms. | `test_sr_02_5_get_is_fast_with_one_million_keys` |

### US-03 — 24/7 Continuous Operation and Recovery After Restart

| ID | Type | Requirement | Checked by |
|----|------|-------------|------------|
| SR-03.1 | Inputs and outputs | Opening an existing log rebuilds the index with no manual step, and each key returns its latest value. | `test_build_index_recovery`, `test_build_index_many_keys_with_multibyte` |
| SR-03.2 | Inputs and outputs | After reopening, a key whose last record is a tombstone returns `None`. | `test_build_index_respects_tombstones` |
| SR-03.3 | Errors | If the log file does not exist, opening the database creates it empty and raises nothing. | `test_build_index_missing_file` |
| SR-03.4 | Errors | If the log cannot be written, `set` raises the `OSError` and the index does not change. | `test_sr_03_4_failed_write_raises_and_keeps_the_index` |
| SR-03.5 | Limits | Opening a log with 1,000,000 records takes under 5 seconds. This value is our proposal and must be confirmed with the client (AC-03.3). | `test_sr_03_5_opens_one_million_records_in_under_5_seconds` |

### What these requirements leave out

- **Records cut by a crash:** if the process stops in the middle of a write, the last line can be incomplete. Today, the database can return a partial value, or fail to open with a `UnicodeDecodeError` if the cut falls inside a multibyte character. Handling this is AC-04.2 in US-04, which is Won't for this delivery.
- **The 24-hour stability test (AC-03.1):** it has not been run, so it has no system requirement yet.

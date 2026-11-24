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
| US-01 | 5 | 8 | 5 | 5 | Performance testing and optimization |
| US-07 | 5 | 5 | 5 | 5 | Compatibility across platforms and UTF-8 |
| US-04 | 8 | 13 | 8 | 8 | Complex failure handling and data integrity |

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
| SR-06.6 | Inputs and outputs | `set` returns `True` once the record is written. `delete` returns `True` if the key existed and `False` if it did not. Added after issue #21. | `tests/test_confirmation.py` |

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

### Decisions that surprised our client

Our client team opened two issues after using PyKV (#21 and #22). Each decision is written here as a system requirement, so the next client reads it before finding it by surprise.

| ID | Type | Requirement | Why | Checked by |
|----|------|-------------|-----|------------|
| SR-06.6 | Inputs and outputs | `set` returns `True` once the record is written. `delete` returns `True` if the key existed and `False` if it did not. | Issue #21 (defect): the caller could not tell a real delete from a delete of a key that did not exist. Fixed in PR #23. | `tests/test_confirmation.py` |
| SR-06.7 | Inputs and outputs | The log separates key and value with the first comma of each line. Keys cannot contain commas (SR-06.3), but values can, and they are returned complete, also after reopening the database. | Issue #22 (decision): the comma is a common character, but it is only forbidden in keys, so the format stays readable as plain text. | `test_sr_06_7_values_with_commas_survive_a_restart` |
| SR-06.2 | Inputs and outputs | `get` on a key that does not exist returns `None` and does not raise `KeyError`. | Same contract as `dict.get`, the most common way to read a key in Python. | `test_non_existent_key` |

---

## 10. Closing E1

E1 was delivered with the tag `v1.0` on `main` (commit `b3c7431`), with the CI green.

### Estimated and completed points

The plan for E1 was Sprints 1 to 3 of section 7. A story counts as completed only if all its system requirements in section 9 pass in `main`.

| ID | Priority | Estimated points | Completed points | Status at the end of E1 |
|----|----------|------------------|------------------|-------------------------|
| US-06 | Must | 3 | 3 | Completed (SR-06.1 to SR-06.5) |
| US-05 | Must | 5 | 5 | Completed (SR-05.1 to SR-05.5) |
| US-02 | Must | 5 | 5 | Completed (SR-02.1 to SR-02.5) |
| US-03 | Must | 5 | 5 | Completed (SR-03.1 to SR-03.5). The 24-hour test (AC-03.1) is left out, as section 9 says |
| US-01 | Should | 5 | 0 | Not completed: `get` is measured with 1,000,000 keys (SR-02.5), but `set` and `delete` are not |
| US-07 | Should | 5 | 0 | Not completed: UTF-8 is tested, but the CI only runs on Linux with Python 3.12, and older machines are not tested |
| **Total** | | **28** | **18** | 64% of the plan |

US-04 (Won't, 8 points) was not planned for E1.

### Velocity

E1 is our first real iteration, so our velocity is **18 points per iteration**: the four Must stories. We planned 28 points, so for E2 we should plan around 18 points instead of 28, and correct the number again with the data of E2.

### Roles

Roles rotate in every delivery, and everyone goes through every role during the course. The roles for E2 are agreed by the team at the start of E2 and recorded here.

---

## 11. Experiment: Log Growth With a Single Key

**Question:** how much does the log grow when the same key is written many times, and how long does it take to rebuild the index?

**How:** `experiments/log_growth.py` writes 1,000,000 values (`value-0` to `value-999999`) to the key `language` in a temporary file, and times `build_index()` with `time.perf_counter()`.

| Measure | Result |
|---------|--------|
| Live keys in the index | 1 |
| Log file size | 21,888,890 bytes (21.9 MB) |
| Time to rebuild the index | 0.43 s (between 0.40 and 0.49 s in 5 more runs on the same file) |

Measured on Windows 11, Python 3.13, a laptop with an Intel i7-13620H.

**What it shows:** the database holds one value, but the log keeps all 1,000,000 records (about 22 bytes each), and opening the database reads all of them. The file and the startup time grow with the number of writes, not with the number of keys. This is the first risk of section 8. Compaction would fix it, but it would delete history that the client asked to keep (R3), so it has to be agreed with the client first.

We also saw that writing the 1,000,000 records took about 400 s (0.4 ms per `set`), because every `set` opens and closes the file.

---

## 12. Phase 2 Backlog (E2)

In phase 2 the log stops being one file that grows forever (the first risk of section 8 and the experiment of section 11). It is split into **segments** with a maximum size, and closed segments are **merged** so that old versions of the same key stop taking space. E2 is delivered with the tag `v2.0` on Tuesday 15 December.

### 12.1 User stories

#### US-08 — Log Split Into Segments With a Maximum Size

> **As** the person who runs PyKV on a server,
> **I want** the log to be split into files with a maximum size,
> **so that** no file grows without limit and old data can be compacted without touching the file that receives the writes.

**Acceptance criteria**

- **AC-08.1 — The active segment closes when it is full**
  - **Given** an active segment that reaches the maximum size,
  - **when** a `set` or a `delete` writes the record that fills it,
  - **then** the segment is closed with the next number (`segment-000001.log`, `segment-000002.log`...) and the next writes go to a new, empty active segment.
- **AC-08.2 — Closed segments are still read**
  - **Given** a key whose last record is in a closed segment,
  - **when** `get(key)` is called,
  - **then** it returns that value, reading only that record.
- **AC-08.3 — Restart in order**
  - **Given** a key written in several segments, and maybe deleted in a newer one,
  - **when** the database is opened again,
  - **then** the index is rebuilt from the oldest segment to the newest, the active one last, and every key returns its newest value (or `None` if its newest record is a tombstone).
- **AC-08.4 — E1 still works**
  - **Given** the tests of E1,
  - **when** they run with segments,
  - **then** all of them pass without changes.

#### US-09 — Automatic Merge With the Generation Rule

> **As** the person who runs PyKV on a server,
> **I want** closed segments to be merged automatically,
> **so that** the disk does not fill up with old versions of the same key and startup does not get slower with every write.

**Acceptance criteria**

- **AC-09.1 — Generation rule**
  - **Given** a segment that has just been closed,
  - **when** the two newest closed segments have the same generation,
  - **then** they are merged into one segment of the next generation, and this is repeated until the two newest have different generations.
- **AC-09.2 — Range names**
  - **Given** a merge of segments 3 and 4,
  - **when** it finishes,
  - **then** the result is called `segment-000003-000004.log`, and its generation can be read from the range (2 segments = generation 1, 4 segments = generation 2).
- **AC-09.3 — Last value of each key**
  - **Given** two segments with several records of the same key,
  - **when** they are merged,
  - **then** the result keeps only the newest record of each key, and `get` returns the same values before and after the merge.

#### US-10 — Safe Merge: Tombstones and Interrupted Merges

> **As** a user of the data,
> **I want** a deleted key to stay deleted after any merge and any restart, and a crash in the middle of a merge not to lose or duplicate data,
> **so that** I can trust what `get` returns.

**Acceptance criteria**

- **AC-10.1 — Tombstones are kept while older data exists**
  - **Given** a merge that does not include the oldest segment,
  - **when** a key's newest record is a tombstone,
  - **then** the tombstone is copied to the merged segment. It is only dropped if the merge includes the oldest segment.
- **AC-10.2 — Delete, merge, restart**
  - **Given** a deleted key,
  - **when** its segments are merged and the database is opened again,
  - **then** `get(key)` returns `None`.
- **AC-10.3 — A crash in the middle of a merge**
  - **Given** a merge that stopped halfway (a temporary file, or the merged segment written but the old ones not deleted yet),
  - **when** the database is opened again,
  - **then** the temporary files and the segments covered by a range are deleted, and every key returns its newest value.

#### US-11 — Sorted Segments With a Memtable and a Sparse Index

> **As** the person who runs PyKV with many keys,
> **I want** segments sorted by key, with a sparse index instead of one entry per key,
> **so that** the index fits in memory on older machines.

Optional for E2 (Daniel, S10). It changes the format of the segments, so if we do it we have to decide it before programming the merge.

### 12.2 Prioritization (MoSCoW)

| ID | Story | Priority (MoSCoW) | Points (proposal) |
|----|-------|-------------------|-------------------|
| US-08 | Log split into segments with a maximum size | Must | 5 |
| US-09 | Automatic merge with the generation rule | Must | 8 |
| US-10 | Safe merge: tombstones and interrupted merges | Must | 5 |
| US-01 | Response in under 500 ms (from E1) | Should | 5 |
| US-07 | Multi-platform, older machines and UTF-8 encoding (from E1) | Should | 5 |
| US-11 | Sorted segments with a memtable and a sparse index | Could | 13 |
| US-04 | Reliability against failures and integrity protection (from E1) | Won't (this time) | 8 |

**MoSCoW check:** the Must stories (US-08, US-09 and US-10) are the three pieces that Daniel requires for E2. They add up to 18 of 49 points (37%), below the 60% limit. US-01 and US-07 stay as Should, as in E1. US-11 is Could because Daniel made it optional. US-04 stays Won't.

### 12.3 Planning Poker

Each member votes on their own with the Fibonacci scale (1, 2, 3, 5, 8, 13). Where the votes do not match, the agreed value is the one chosen by two of the three members, as in section 5.1. The points in 12.2 are a proposal until the three columns are filled in.

| ID | Alejandro | Gabriel | Jorge | Agreed | Justification |
|----|-----------|---------|-------|--------|---------------|
| US-08 | 5 | | | | Close the active segment, read closed segments, rebuild in order |
| US-09 | 8 | | | | Generation rule, range names and keeping the last value of each key |
| US-10 | 5 | | | | Tombstone rule, temporary file with `os.replace`, cleanup on startup |
| US-11 | 13 | | | | New segment format, memtable, sparse index and a different merge |

### 12.4 How many sprints phase 2 needs

Our velocity in E1 was **18 points per sprint** (section 10).

| What we plan | Points | Sprints (points / 18, rounded up) |
|--------------|--------|-----------------------------------|
| Must (US-08, US-09, US-10) | 18 | 1 |
| Must + Should (+ US-01, US-07) | 28 | 2 |
| Everything except Won't (+ US-11) | 41 | 3 |

The Must stories fit in one sprint, so that is the plan for E2. US-01 and US-07 go to a second sprint if there is time before 15 December. US-11 is left out of E2.

### 12.5 Work order

| Order | Story | Who | Branch | Starts from |
|-------|-------|-----|--------|-------------|
| 1 | US-08 | Gabriel | `feat/segments` | `main` |
| 2 | US-09 and US-10 | Jorge | `feat/merge` | `feat/segments`, once it is merged |

The merge needs the segments, so Jorge's branch starts when Gabriel's pull request is in `main`.

### 12.6 System requirements for phase 2

The maximum size and the merge rule are also written in the README, because they change how the database is used.

| ID | Story | Type | Requirement | Checked by |
|----|-------|------|-------------|------------|
| SR-08.1 | US-08 | Limits | The active segment is closed when its size reaches 1 MiB (1,048,576 bytes). The size can be changed with `Database(path, max_segment_size=...)`. | `test_active_segment_closes_at_the_maximum_size`, `test_writes_continue_in_a_new_active_segment` |
| SR-08.2 | US-08 | Inputs and outputs | The active segment is the file given to `Database`. Closed segments are in the folder `<file>.segments`, named `segment-000001.log`, `segment-000002.log`..., and a closed segment is never renamed. | `test_segment_names_keep_their_number_and_range` |
| SR-08.3 | US-08 | Inputs and outputs | `get` reads the record of the key in the segment where the index says it is, without reading the other segments. | `test_get_reads_closed_segments` |
| SR-08.4 | US-08 | Inputs and outputs | On startup, the index is rebuilt from the oldest closed segment to the newest, and the active segment last. | `test_restart_rebuilds_the_index_in_order`, `test_tombstone_in_a_newer_segment_survives_restart` |
| SR-09.1 | US-09 | Inputs and outputs | After closing a segment, while the two newest closed segments have the same generation, they are merged into one. | `test_generation_rule` |
| SR-09.2 | US-09 | Inputs and outputs | A merged segment is named after the range it replaces (`segment-000001-000004.log`). Its generation is log2 of the number of segments in the range. | `test_generation_comes_from_the_range` |
| SR-09.3 | US-09 | Inputs and outputs | A merged segment keeps only the newest record of each key. | `test_merge_keeps_the_last_value_of_each_key` |
| SR-09.4 | US-10 | Inputs and outputs | A tombstone is only dropped in a merge that includes the oldest closed segment. In any other merge, it is copied. | `test_tombstone_survives_merge_and_restart`, `test_merge_without_the_oldest_segment_keeps_the_tombstone` |
| SR-09.5 | US-10 | Errors | A merge writes to a temporary file, calls `os.fsync` and renames it with `os.replace`, and only then deletes the old segments. On startup, temporary files and segments covered by a range are deleted. | `test_restart_cleans_up_an_interrupted_merge` |

### 12.7 To agree with the client

- **The merge deletes history.** In E1 the client asked to keep every insertion, modification and deletion (R3, US-05). A merge keeps only the last record of each key, so the old versions in closed segments disappear. The active segment still keeps everything. We have to ask the client if this is acceptable, or if the history has to be copied somewhere else before merging.
- **The maximum size of 1 MiB** is our proposal. With the experiment of section 11 (21.9 MB for 1,000,000 writes), it means about 21 segments before merging.

### 12.8 Roles for E2

Daniel asked to give each role to someone who did not have it in E1, and to keep the roles until E2 is delivered. The team agrees on them and records them here.

| Role | E2 |
|------|----|
| Product Owner | |
| Scrum Master | |
| Developers | |

### 12.9 Lab sprint (24 November): review and retrospective

To be filled in by the team: the sprint goal, whether it was met, what worked, what did not, and the improvement we choose for the next sprint.

| | |
|---|---|
| Sprint goal | |
| Was it met? | |
| What worked | |
| What did not work | |
| Improvement chosen | |

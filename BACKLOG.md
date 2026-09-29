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

A story is considered done when:

1. The code is merged into the main branch through a Pull Request reviewed by at least one teammate.
2. All acceptance criteria are covered by automated tests that pass.
3. The tests do not reduce overall coverage below the threshold agreed by the team.
4. The code follows the PEP 8 style guide.
5. Documentation (README and docstrings) is up to date.
6. The Product Owner has validated the story in the sprint review.

---

## 5. Backlog Summary

| ID | Story | Requirement | Priority (MoSCoW) | Points | Suggested sprint |
|----|-------|-------------|-------------------|--------|------------------|
| US-06 | Simple API for Python programmers | R4 | Must | 3 | 1 |
| US-01 | Response in under 500 ms | R1 | Must | 5 | 1 |
| US-05 | Append-only historical log and tombstones | R3 | Must | 5 | 1 |
| US-02 | In-memory hash index for large volumes | R1 | Must | 5 | 2 |
| US-03 | 24/7 continuous operation and recovery after restart | R2 | Must | 5 | 2 |
| US-04 | Reliability against failures and integrity protection | R2 | Must | 8 | 3 |
| US-07 | Multi-platform, older machines and UTF-8 encoding | R5 | Must | 5 | 3 |

*Estimates in story points (Fibonacci scale), to be refined in a Planning Poker session.*

---

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
| Sprint 3 | US-04, US-07 | Robustness against failures and multi-platform compatibility with UTF-8 |

## 8. Identified Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| The log grows indefinitely due to its append-only nature | Higher disk usage and slower startups | Register log compaction as a future story, provided it does not go against the client's audit requirement (R3) |
| The whole index must fit in memory | Limit on older machines | Document the maximum supported volume (AC-07.3) |
| Guaranteeing persistence may affect latency | Risk to the 500 ms target | Measure both objectives together in the US-01 and US-04 tests |
| Poorly defined qualitative requirements | Rework | Validate the assumptions in section 3 in the first review with the client |

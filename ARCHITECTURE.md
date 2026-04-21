# AILC-SFTP Architecture

AILC-SFTP is a deterministic, “AI-ready” SFTP engine that wraps a standard SSH/SFTP server with:

- **Decoupled storage adapters** (local disk, S3/MinIO, future cloud targets)
- **Math-based integrity guarantees** (SHA-256 sidecar manifests)
- **Structured, correlation-aware logging** (JSON logs with `correlation_id`)
- **Client-side orchestration** (resumable uploads + integrity verification)

This document describes the core components and how they interact.

---

## 1. High-level overview

At a high level, AILC-SFTP consists of:

- **SFTP Server (`sftp_server.py`)**
  - Implements the SFTP protocol using Paramiko.
  - Uses a custom `AILCDiskInterface` and `LocalFileHandle`.
  - Writes uploaded files into a configurable storage root.
  - On file close, computes a **SHA-256 hash** and writes a `<filename>.sha256` sidecar.

- **SFTP Agent / Client (`sftp_agent.py`)**
  - Connects to the SFTP server using credentials from `.env`.
  - Performs resumable uploads (partial transfer resume).
  - After upload, verifies integrity by comparing:
    - Local file hash
    - Remote sidecar hash (`<remote_name>.sha256`)

- **Storage Abstraction (`storage_interface.py`, `local_storage.py`, `s3_storage.py`)**
  - `BaseStorage` defines the contract for storage backends.
  - `LocalStorage` writes to local disk.
  - `S3Storage` writes to S3/MinIO (endpoint configurable).
  - Future backends (Azure, GCP, NFS, etc.) can be added without touching SFTP logic.

- **Integrity Utilities (`hasher.py`)**
  - Provides `generate_sha256(data: bytes)` and `hash_file(filepath: str)` helpers.
  - Used by both server and storage to compute hashes.

- **Structured Logging (`logger.py`)**
  - JSON logs with:
    - `timestamp`
    - `level`
    - `message`
    - `correlation_id`
    - `module`
  - Designed for downstream ingestion by log pipelines or AI-based anomaly detection.

---

## 2. Control flow: upload lifecycle

### 2.1 Client-side (SFTP Agent)

1. **Prepare file**
   - Local file is created or selected.
   - Local SHA-256 hash is computed (`get_file_hash`).

2. **Connect**
   - Agent reads `SFTP_USER`, `SFTP_PASS`, `SFTP_PORT` from `.env`.
   - Establishes a Paramiko `Transport` to `127.0.0.1:<PORT>`.

3. **Upload (resumable)**
   - `resumable_upload` checks if a partial remote file exists.
   - If present, resumes from the last byte.
   - Writes in chunks until complete.

4. **Size check**
   - Agent compares local file size vs remote file size via `sftp.stat`.

5. **Integrity verification**
   - Agent reads `<remote_name>.sha256` from the server.
   - Compares local hash vs remote hash.
   - Returns a `TransferResult` with:
     - `success`
     - `bytes_transferred`
     - `local_hash`
     - `remote_hash`
     - `error_log` (if any)

### 2.2 Server-side (SFTP Server)

1. **Connection accepted**
   - `MySFTPServer` listens on `host:port`.
   - Loads or generates an RSA host key (`sftp_server.key`).
   - Uses `AILCServerInterface` for authentication:
     - Username/password from `.env`.

2. **File open**
   - `AILCDiskInterface.open`:
     - Normalizes the path.
     - Resolves it under `storage.base_path` (e.g., `./sftp_root`).
     - Returns a `LocalFileHandle`.

3. **File write**
   - `LocalFileHandle.write`:
     - Uses `os.lseek` + `os.write` to write bytes.
     - Logs file open events with `correlation_id`.

4. **File close + hash generation**
   - `LocalFileHandle.close`:
     - Closes the file descriptor.
     - Skips hashing if the file is already a `.sha256`.
     - Computes SHA-256 via `hash_file`.
     - Writes `<filename>.sha256` sidecar.
     - Logs success or failure with `correlation_id` and `sha256`.

---

## 3. Storage abstraction

### 3.1 Base interface

`storage_interface.py` defines:

- `save(file_name: str, data: bytes) -> bool`
- `exists(file_name: str) -> bool`
- `get_hash(file_name: str) -> str`

This allows the SFTP engine to remain agnostic to:

- Local disk
- S3/MinIO
- Future storage systems

### 3.2 LocalStorage

- Writes files under a configured `base_path`.
- Ensures directory exists.
- Uses `hash_file` to compute hashes for existing files.

### 3.3 S3Storage (MinIO-ready)

- Uses `boto3` with a configurable `endpoint_url`.
- Designed to work with:
  - MinIO on a laptop
  - S3-compatible endpoints
- Creates bucket if it doesn’t exist.
- Implements `save` and `exists`.

> Note: S3Storage is wired for future use; the current POC primarily uses `LocalStorage`.

---

## 4. Integrity model

The integrity model is based on **math-based truth**:

- Every file written by the SFTP server is accompanied by a **SHA-256 sidecar**.
- The client independently computes the SHA-256 of the local file.
- The client reads the remote sidecar and compares hashes.
- If hashes match:
  - Integrity is verified.
- If hashes differ or sidecar is missing:
  - Transfer is considered failed.

This pattern:

- Prevents silent corruption.
- Enables deterministic verification.
- Creates a foundation for AI-based anomaly detection (e.g., repeated mismatches, missing manifests).

(A separate `INTEGRITY_MODEL.md` will go deeper into this.)

---

## 5. Observability model

All logs are:

- JSON-formatted.
- Emitted via a shared `logger` instance.
- Enriched with:
  - `correlation_id` (per session)
  - `module`
  - Optional `sha256` on success.

This enables:

- Easy ingestion into log pipelines.
- Correlation of events across:
  - Authentication
  - File open/close
  - Hash generation
  - Client verification
- Future AI-based anomaly detection on:
  - Unusual patterns
  - Repeated failures
  - Suspicious access patterns

(A separate `OBSERVABILITY.md` will detail log shapes and examples.)

---

## 6. Trust boundaries

- **Inside trust boundary**
  - SFTP server process
  - Storage adapter
  - Local disk / MinIO endpoint
  - Hashing utilities

- **Outside trust boundary**
  - SFTP clients
  - Network
  - External automation/orchestration

The design assumes:

- Credentials are managed via `.env` (not committed).
- Host key is generated locally and persisted as `sftp_server.key`.
- Storage backends may be remote but are accessed via well-defined adapters.

---

## 7. Future evolution

Planned roadmap (from `ROADMAP.md`):

1. Observability & Truth (JSON logs, correlation IDs)
2. Programmable Plumbing (storage abstraction)
3. Data Integrity (SHA-256 manifests) ✅
4. Stateful Resilience (partial transfer resume) ✅ POC in `sftp_agent.py`
5. Zero Trust Identity (key-based auth, vault integration)
6. API-First Orchestration (FastAPI wrapper)
7. Strategic Documentation (this file + diagrams + GitHub Pages)

AILC-SFTP is intentionally small but structured, so it can evolve into:

- A teaching artifact for AI-era file transfer patterns.
- A foundation for enterprise-grade, AI-observable SFTP workflows.


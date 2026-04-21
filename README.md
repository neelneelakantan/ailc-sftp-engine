# AILC‑SFTP — Deterministic, Observable, AI‑Ready SFTP Engine (2026)

AILC‑SFTP is a modern rethinking of SFTP for 2026:  
a **deterministic, observable, cloud‑agnostic, AI‑ready** file transfer engine built on top of the familiar SSH/SFTP protocol.

It is intentionally small, understandable, and teachable — a reference architecture for how legacy protocols can be upgraded with:

- **math‑based integrity (SHA‑256 manifests)**  
- **structured JSON observability**  
- **resumable uploads**  
- **storage abstraction (Local, S3/MinIO, future Azure/GCP)**  
- **AI‑ready telemetry for anomaly detection**  

This project demonstrates how deterministic systems and probabilistic systems can safely coexist.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install paramiko python-dotenv boto3
```

### 2. Configure environment
Copy `.env.example` → `.env` and set:

```
SFTP_USER=<username>
SFTP_PASS=<password>
SFTP_PORT=3373
STORAGE_TYPE=LOCAL   # or S3
```

### 3. Start the server
```bash
python sftp_server.py
```

### 4. Run the client/agent
```bash
python sftp_agent.py
```

Uploads will automatically:

- resume if partially transferred  
- generate a SHA‑256 sidecar on the server  
- verify integrity end‑to‑end  

---

## 🏗️ Architecture Overview

AILC‑SFTP consists of four core layers:

### **1. SFTP Server (Paramiko-based)**
- Custom `AILCDiskInterface` and `LocalFileHandle`
- Writes files into a storage backend
- Generates `<filename>.sha256` on file close
- Emits structured JSON logs with correlation IDs

### **2. SFTP Agent / Client**
- Performs resumable uploads
- Computes local SHA‑256
- Reads remote sidecar manifest
- Verifies integrity deterministically

### **3. Storage Abstraction**
- `BaseStorage` defines the contract
- `LocalStorage` for disk
- `S3Storage` for S3/MinIO
- Future: Azure, GCP, NFS, encrypted storage

### **4. Observability Layer**
- JSON logs
- Correlation IDs
- AI‑ready telemetry
- Deterministic breadcrumbs across server + client

Full details in:

- `ARCHITECTURE.md`
- `INTEGRITY_MODEL.md`
- `OBSERVABILITY.md`
- `STORAGE_ADAPTERS.md`

---

## 🔐 Integrity Model (Math‑Based Truth)

Every uploaded file produces:

```
<filename>
<filename>.sha256
```

The client:

1. Computes local SHA‑256  
2. Uploads file (resumable)  
3. Reads remote sidecar  
4. Compares hashes  

If they match → **integrity verified**  
If not → **transfer rejected**

This prevents:

- silent corruption  
- partial writes  
- tampering  
- storage inconsistencies  

---

## 📊 Observability (AI‑Ready)

All logs are structured JSON:

```json
{
  "timestamp": "...",
  "level": "INFO",
  "message": "Integrity Verified: remote_test.txt",
  "correlation_id": "uuid",
  "module": "sftp_server",
  "sha256": "..."
}
```

This enables:

- deterministic debugging  
- audit trails  
- anomaly detection  
- LLM-based log summarization  
- future OpenTelemetry integration  

---

## ☁️ Storage Backends

### Local Disk (default)
Simple, fast, ideal for development.

### S3 / MinIO
S3-compatible backend for:

- cloud deployments  
- local MinIO testing  
- air‑gapped environments  

### Future Backends
The architecture supports:

- Azure Blob  
- Google Cloud Storage  
- NFS / SMB  
- Encrypted storage  
- Immutable storage  

---

## 🧭 Roadmap (Strategic)

1. **Observability & Truth**  
2. **Programmable Plumbing (Storage Abstraction)**  
3. **Data Integrity (SHA‑256 Manifests)**  
4. **Stateful Resilience (Resumable Uploads)**  
5. **Zero‑Trust Identity (Key‑based Auth, Vault Integration)**  
6. **API‑First Orchestration (FastAPI Trigger Layer)**  
7. **Strategic Documentation & Diagrams**  

---

## 🎯 Purpose of This Project

AILC‑SFTP is a **reference artifact**, not a product.  
It demonstrates:

- clean architecture  
- deterministic guarantees  
- AI‑ready observability  
- cloud‑agnostic design  
- modernization patterns for legacy protocols  

It shows how even a decades‑old protocol can be transformed into a **trustworthy, observable, intelligent data movement engine**.

---

## 📄 License

MIT License

### **LICENSE.md (MIT)**  
or  
### **LinkedIn Project Description**

Just say **“next license”** or **“next LinkedIn”**.
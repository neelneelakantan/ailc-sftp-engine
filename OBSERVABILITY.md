# AILC-SFTP Observability Model

Observability in AILC‑SFTP is not an afterthought — it is a **first‑class architectural pillar**.  
The system emits structured, correlation-aware logs designed for:

- deterministic debugging  
- auditability  
- anomaly detection  
- AI‑driven pattern analysis  
- future integration with log pipelines (ELK, OpenTelemetry, etc.)

This document explains how observability works across the server, client, and storage layers.

---

## 1. Goals of the Observability Layer

The observability model is designed to provide:

### **1. End-to-end traceability**
Every upload, hash generation, and verification step is tied together using a `correlation_id`.

### **2. Machine-readable logs**
All logs are JSON — no free‑form text, no ambiguity.

### **3. Deterministic breadcrumbs**
Logs capture:
- file open/close events  
- byte writes  
- hash generation  
- manifest creation  
- verification results  
- authentication outcomes  

### **4. AI-ready structure**
The logs are intentionally shaped so that:
- anomaly detection models  
- LLM-based log summarizers  
- pattern detectors  

can easily ingest and reason about them.

---

## 2. JSON Log Format

All logs follow this structure:

```json
{
  "timestamp": "2026-03-31T20:15:42.123Z",
  "level": "INFO",
  "message": "Upload completed successfully: remote_test.txt",
  "correlation_id": "c1b0e8f4-3f1e-4c8d-9f0c-1b2f7f8e9d12",
  "module": "sftp_server",
  "sha256": "a3f4...9c1d"   // optional
}
```

### **Key fields**

| Field | Purpose |
|-------|---------|
| `timestamp` | UTC timestamp for ordering and replay |
| `level` | INFO / ERROR / WARNING |
| `message` | Human-readable event description |
| `correlation_id` | Ties all events in a session together |
| `module` | Source module (server, agent, storage, etc.) |
| `sha256` | Included only when integrity is verified |

This structure ensures logs are both human-friendly and machine-friendly.

---

## 3. Correlation IDs

Every SFTP session receives a unique `correlation_id`:

```python
session_id = str(uuid.uuid4())
```

This ID is injected into:

- authentication logs  
- file open events  
- file close events  
- hash generation  
- manifest creation  
- client verification  

This allows:

- replaying a full transfer  
- grouping logs across modules  
- identifying multi-step failures  
- feeding logs into AI systems for anomaly detection  

### Example

```
📂 SFTP Open Request: remote_test.txt
📄 File opened: ./sftp_root/remote_test.txt
✅ Integrity Verified: remote_test.txt
```

All three share the same `correlation_id`.

---

## 4. Server-Side Observability

The server logs:

### **Authentication**
- success/failure  
- username  
- correlation ID  

### **File lifecycle**
- file open  
- file write  
- file close  
- hash generation  
- manifest creation  

### **Storage adapter events**
- save success/failure  
- S3/MinIO upload errors  
- local disk write errors  

### **Integrity events**
- SHA‑256 computed  
- manifest written  
- hash failures  

These logs form the “ground truth” of the server.

---

## 5. Client-Side Observability

The client logs:

### **Connection events**
- connection attempts  
- authentication errors  
- transport failures  

### **Upload lifecycle**
- resumable upload detection  
- chunk writes  
- partial resume offsets  

### **Verification**
- local hash  
- remote hash  
- mismatch detection  
- manifest missing/empty  

### **Final result**
The `TransferResult` object is logged as JSON.

This gives you a full picture of the transfer from the client’s perspective.

---

## 6. Storage Adapter Observability

Each storage backend logs:

- file save attempts  
- file save success/failure  
- hash retrieval  
- bucket creation (S3/MinIO)  
- object existence checks  

This ensures that storage issues are visible and diagnosable.

---

## 7. AI-Ready Observability

The logs are intentionally shaped for AI systems.

### **Patterns AI can detect**
- repeated hash mismatches  
- missing manifests  
- abnormal file sizes  
- repeated partial uploads  
- suspicious access patterns  
- unusual timing between events  
- repeated authentication failures  

### **Why JSON matters**
LLMs and anomaly detectors perform best when logs are:

- structured  
- consistent  
- predictable  
- correlation-aware  

AILC‑SFTP is designed for this from day one.

---

## 8. Future Enhancements

Planned observability improvements:

- OpenTelemetry exporters  
- FastAPI `/health` and `/metrics` endpoints  
- Prometheus counters (uploads, failures, retries)  
- Trace IDs for multi-hop workflows  
- Log sampling for high-volume environments  
- AI-based anomaly scoring  

These will be added in future roadmap sprints.

---

## 9. Summary

The observability model provides:

- structured JSON logs  
- correlation-aware tracing  
- deterministic breadcrumbs  
- AI-ready telemetry  
- full visibility across server, client, and storage  

This elevates AILC‑SFTP from a simple SFTP wrapper to a **verifiable, observable, and intelligent data movement engine**.



# **FUTURE_WORK.md**  
### *Planned Enhancements and Implementation Roadmap for AILC‑SFTP (2026–2027)*

This document outlines the **planned**, **in‑progress**, and **near‑term** enhancements for AILC‑SFTP.  
These items extend the deterministic core and prepare the system for the agentic behaviors described in `NORTH_STAR.md`.

This is an implementation roadmap — not a commitment and not a product plan.

---

## **1. Observability Enhancements**

### **1.1 OpenTelemetry Exporters**  
Add OTLP exporters for:

- traces  
- metrics  
- structured logs  

This enables integration with:

- Grafana  
- Honeycomb  
- Datadog  
- Elastic  

### **1.2 Prometheus Metrics**  
Expose counters for:

- uploads  
- failures  
- retries  
- manifest generation  
- hash mismatches  

### **1.3 `/health` and `/metrics` Endpoints**  
Expose FastAPI endpoints for:

- liveness  
- readiness  
- metrics scraping  

---

## **2. Storage Backend Expansion**

### **2.1 Azure Blob Storage**  
Implement `AzureBlobStorage` backend.

### **2.2 Google Cloud Storage**  
Implement `GCPStorage` backend.

### **2.3 NFS / SMB Support**  
Add enterprise file system support for on‑prem deployments.

### **2.4 Encrypted Storage Layers**  
Add AES‑GCM or envelope encryption for sensitive workloads.

### **2.5 Immutable / Versioned Storage**  
Support WORM or Git‑like versioned storage for regulated industries.

---

## **3. Identity & Security**

### **3.1 Zero‑Trust Identity**  
Move from username/password to:

- SSH key‑pair auth  
- dynamic key loading  
- Vault‑based credential retrieval  

### **3.2 Policy‑Driven Access Controls**  
Introduce a small policy engine for:

- allowed paths  
- allowed file types  
- size limits  
- retention rules  

---

## **4. API‑First Orchestration**

### **4.1 FastAPI Trigger Layer**  
Expose APIs for:

- triggering uploads  
- querying transfer history  
- retrieving manifests  
- retrieving logs by correlation_id  

### **4.2 Webhook Integration**  
Emit events to:

- workflow engines  
- automation systems  
- monitoring dashboards  

---

## **5. Agentic Layer Foundations**

These are **not** the aspirational behaviors — those live in `NORTH_STAR.md`.  
These are the *practical building blocks* needed to support them.

### **5.1 Log Normalization Pipeline**  
Normalize logs for downstream ML ingestion.

### **5.2 Anomaly Signature Library**  
Define deterministic anomaly signatures:

- missing manifests  
- repeated partial uploads  
- abnormal timing gaps  
- repeated auth failures  

### **5.3 Session Summaries**  
Generate structured summaries for:

- transfer sessions  
- anomalies  
- integrity outcomes  

### **5.4 Policy‑Bound Recommendations**  
Allow the agentic layer to recommend:

- retry  
- escalate  
- quarantine  
- notify operator  

without executing actions automatically.

---

## **6. Developer Experience**

### **6.1 GitHub Pages Documentation**  
Publish:

- architecture diagrams  
- design philosophy  
- integrity model  
- observability model  
- agentic overlay  
- north star vision  

### **6.2 Example Workflows**  
Add sample scripts for:

- resumable uploads  
- S3/MinIO usage  
- Azure/GCP usage  
- anomaly detection demos  

---

## **7. Testing & Hardening**

### **7.1 Scenario Testing Harness**  
Simulate:

- partial writes  
- network interruptions  
- storage failures  
- hash mismatches  

### **7.2 Performance Benchmarks**  
Measure:

- throughput  
- latency  
- manifest generation cost  
- storage backend performance  

### **7.3 Chaos Testing**  
Inject:

- random disconnects  
- slow writes  
- corrupted chunks  

to validate resilience.

---

## **8. Related Documents**

- `ARCHITECTURE.md` — deterministic core  
- `AGENTIC_OVERLAY.md` — current agentic model  
- `NORTH_STAR.md` — aspirational agentic behaviors  
- `OBSERVABILITY.md` — telemetry model  
- `INTEGRITY_MODEL.md` — math-based truth  


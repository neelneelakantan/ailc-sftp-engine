
# **AGENTIC_OVERLAY.md**  
### *Agentic AI Overlay — Deterministic Core + Probabilistic Sidecar*

AILC‑SFTP supports an **agentic AI sidecar** that observes deterministic signals emitted by the SFTP engine and provides optional, policy‑driven intelligence.  
This document describes the **overlay model**, not future behavior.  
It defines how the agentic layer *sits beside* the deterministic core without modifying protocol semantics.

---

## **1. Purpose of the Overlay**

The agentic layer exists to:

- observe deterministic events  
- analyze structured telemetry  
- detect anomalies  
- summarize sessions  
- recommend operator actions  

It does **not** alter:

- SFTP protocol behavior  
- hashing logic  
- storage semantics  
- trust boundaries  

The deterministic core remains the source of truth.

---

## **2. Architectural Model (Stick Diagram)**

```text
+--------------------------------------------------------------+
|                 AGENTIC AI OVERLAY MODEL                     |
|        Deterministic Core + Probabilistic Sidecar            |
+--------------------------------------------------------------+

                 +-------------------------------+
                 |   DETERMINISTIC CORE          |
                 |          (AILC-SFTP)          |
                 +-------------------------------+
                 | - Paramiko SFTP server        |
                 | - Storage adapters            |
                 | - SHA-256 sidecar hashes      |
                 | - Resumable uploads           |
                 | - JSON logs (correlation_id)  |
                 +-------------------------------+
                               |
                               v
                 +-------------------------------+
                 |      EXECUTION PIPELINE       |
                 |   (What must happen)          |
                 +-------------------------------+
                 | - File open/write/close       |
                 | - Sidecar generation          |
                 | - Client integrity checks     |
                 | - Structured telemetry        |
                 +-------------------------------+
                               |
                     events / logs / hashes
                               v
+--------------------------------------------------------------+
|        PROBABILISTIC SIDECAR (AGENTIC LAYER)                 |
+--------------------------------------------------------------+
| - Observes JSON logs + hashes                                |
| - Detects anomalies (retries, failures, missing sidecars)    |
| - Learns temporal patterns                                   |
| - Suggests actions (retry, escalate, quarantine)             |
| - Produces operator summaries                                |
+--------------------------------------------------------------+
                               |
                     recommendations / warnings
                               v
+--------------------------------------------------------------+
|                    GOVERNANCE (AILC)                         |
+--------------------------------------------------------------+
| - Evaluation harness                                         |
| - Scenario testing                                           |
| - Safety envelopes / policies                                |
| - Versioning and temporal snapshots                          |
| - Human-in-the-loop checkpoints                              |
+--------------------------------------------------------------+
```

---

## **3. Deterministic Core (Ground Truth)**

The agentic layer relies on deterministic signals defined in:

- `ARCHITECTURE.md`  
- `INTEGRITY_MODEL.md`  
- `OBSERVABILITY.md`  

These include:

- SHA‑256 sidecar manifests  
- structured JSON logs  
- correlation IDs  
- file lifecycle events  
- storage adapter events  

The core is **immutable** from the agent’s perspective.

---

## **4. Sidecar Responsibilities (Probabilistic Layer)**

The agentic sidecar:

- consumes logs  
- correlates events  
- identifies anomalies  
- summarizes sessions  
- recommends operator actions  

It does **not**:

- modify files  
- alter protocol behavior  
- bypass hashing  
- override storage semantics  
- break trust boundaries  

It is an **observer + advisor**, not an executor.

---

## **5. Governance Layer (AILC)**

The governance layer defines:

- evaluation harness  
- scenario testing  
- safety envelopes  
- versioning of agentic behavior  
- human‑in‑the‑loop checkpoints  

This ensures the agentic layer remains predictable and bounded.

---

## **6. Trust Boundaries**

**Inside trust boundary:**

- hashing  
- storage adapters  
- manifest generation  
- deterministic logs  

**Outside trust boundary:**

- agentic sidecar  
- network  
- client machines  
- external automation  

The agentic layer cannot silently corrupt or modify data.

---

## **7. Relationship to NORTH_STAR.md**

This file describes the **current conceptual overlay**, not future capabilities.  
Aspirational behaviors (e.g., predictive failure detection, workflow correlation, optimizer logic) live in:

- `NORTH_STAR.md`  
- `FUTURE_WORK.md`  

This keeps the architecture honest and clean.

---

## **8. Related Documents**

- `ARCHITECTURE.md` — deterministic core  
- `INTEGRITY_MODEL.md` — math-based truth  
- `OBSERVABILITY.md` — telemetry model  
- `NORTH_STAR.md` — aspirational agentic behaviors  
- `FUTURE_WORK.md` — planned enhancements  

---

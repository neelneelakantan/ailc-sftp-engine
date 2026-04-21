# AILC-SFTP Integrity Model

The integrity model is the core of AILC‑SFTP. It ensures that every file transfer is validated using **math-based truth**, not assumptions, timestamps, or protocol guarantees. This document explains how integrity is enforced, why SHA‑256 sidecars exist, and how the client and server collaborate to detect corruption, partial writes, or tampering.

---

## 1. Why Integrity Matters

Traditional SFTP has two major weaknesses:

1. **Silent corruption**  
   Network interruptions, partial writes, or disk issues can produce incomplete files without raising errors.

2. **No built-in verification**  
   SFTP does not provide a native checksum or manifest mechanism.

AILC‑SFTP solves this by adding a deterministic verification layer:

> **Every file written by the server produces a SHA‑256 manifest.  
> Every client compares its own hash with the server’s manifest.**

This creates a cryptographic handshake between client and server.

---

## 2. The Integrity Pipeline (End-to-End)

### **Step 1 — Client computes local SHA‑256**
Before upload:

```
local_hash = sha256(local_file)
```

This is the “ground truth” for the file.

### **Step 2 — Server writes file**
The SFTP server writes bytes using `LocalFileHandle.write`.

### **Step 3 — Server generates sidecar manifest**
When the file is closed:

```
<filename>
<filename>.sha256
```

The server computes:

```
remote_hash = sha256(file_on_disk)
```

And writes it to:

```
<filename>.sha256
```

This is the server’s “mathematical truth.”

### **Step 4 — Client reads the manifest**
After upload, the client opens:

```
remote_name + ".sha256"
```

and reads the server’s hash.

### **Step 5 — Client compares hashes**

```
if local_hash == remote_hash:
    integrity = VERIFIED
else:
    integrity = FAILED
```

This is the deterministic brake — the transfer is only considered successful if the math matches.

---

## 3. Why SHA‑256?

SHA‑256 is:

- collision-resistant  
- widely supported  
- fast enough for large files  
- deterministic across platforms  
- safe for long-term archival workflows  

It is the industry standard for:

- S3 ETag verification  
- container image integrity  
- artifact signing  
- blockchain hashing  

Using SHA‑256 aligns AILC‑SFTP with modern integrity expectations.

---

## 4. Sidecar Manifest Design

Each uploaded file produces a sidecar:

```
<filename>.sha256
```

Contents:

```
<64-character hex SHA-256>
```

### **Why a sidecar file?**

- Avoids modifying the original file  
- Easy to inspect manually  
- Easy for automation to parse  
- Works across all storage backends  
- Plays well with S3/MinIO object stores  
- Avoids metadata inconsistencies  

This pattern is used by:

- Kubernetes  
- OCI container registries  
- Artifact repositories  
- Backup systems  

---

## 5. Failure Modes Detected

The integrity model detects:

### **1. Partial uploads**
If the server wrote fewer bytes than the client:

- size mismatch  
- hash mismatch  

### **2. Corrupted uploads**
If any byte differs:

- hash mismatch  

### **3. Missing manifests**
If the server failed to generate the sidecar:

- client retries for 2 seconds  
- then fails with `Manifest empty/missing`

### **4. Tampering**
If a file is modified after upload:

- hash mismatch  

### **5. Storage backend issues**
If S3/MinIO or disk writes are inconsistent:

- hash mismatch  
- missing manifest  

This gives you a deterministic safety net.

---

## 6. Trust Boundary

### **Inside trust boundary**
- Server hashing logic  
- Storage adapter  
- Sidecar generation  
- Local hashing utilities  

### **Outside trust boundary**
- Network  
- SFTP protocol  
- Client machine  
- External automation  

The integrity model ensures that **anything outside the trust boundary cannot silently corrupt data**.

---

## 7. AI-Ready Integrity

Because all logs are JSON with correlation IDs, AI systems can detect:

- repeated hash mismatches  
- missing manifests  
- unusual file sizes  
- suspicious access patterns  
- repeated partial uploads  
- anomalies in transfer timing  

This is the foundation for:

- anomaly detection  
- automated remediation  
- predictive failure analysis  
- intelligent retry strategies  

AILC‑SFTP is intentionally designed to be “AI-observable.”

---

## 8. Summary

The integrity model provides:

- deterministic verification  
- cryptographic truth  
- tamper detection  
- silent corruption prevention  
- AI-ready observability  

This elevates SFTP from a “best effort” protocol to a **verifiable, trustworthy data movement layer**.




# Storage Adapters in AILC‑SFTP

AILC‑SFTP uses a clean, extensible storage abstraction to decouple the SFTP protocol layer from the underlying storage system.  
This allows the engine to support:

- Local disk  
- S3 / MinIO  
- Future cloud storage (Azure Blob, GCP Storage)  
- NFS or enterprise file systems  
- Encrypted storage layers  

All without modifying the SFTP server logic.

This document explains the design, the contract, and how to extend the system.

---

## 1. Design Goals

The storage layer is built around four principles:

### **1. Decoupling**
SFTP logic should not know or care where files are stored.

### **2. Replaceability**
Storage backends should be swappable with zero changes to the server.

### **3. Observability**
All storage operations should emit structured logs.

### **4. Integrity**
Storage backends must support hash retrieval for verification.

---

## 2. Base Interface (`BaseStorage`)

All storage backends implement the same abstract interface:

```python
class BaseStorage(ABC):
    @abstractmethod
    def save(self, file_name: str, data: bytes) -> bool:
        pass

    @abstractmethod
    def exists(self, file_name: str) -> bool:
        pass

    @abstractmethod
    def get_hash(self, file_name: str) -> str:
        pass
```

### **Why this matters**

- The SFTP server can call `storage.save()` without knowing the backend.
- The integrity layer can call `storage.get_hash()` consistently.
- New backends can be added without touching SFTP code.

This is the “programmable plumbing” layer from the roadmap.

---

## 3. LocalStorage

`local_storage.py` implements the simplest backend: writing to local disk.

### **Key behaviors**

- Ensures the base directory exists.
- Writes files using standard Python I/O.
- Computes SHA‑256 using `hash_file`.
- Emits JSON logs on success/failure.

### **Use cases**

- Local development  
- Laptop-based testing  
- Edge deployments  
- Environments without object storage  

### **Example**

```python
storage = LocalStorage(base_path="./sftp_root")
```

This is the default backend used by the POC.

---

## 4. S3Storage (MinIO-ready)

`s3_storage.py` implements an S3-compatible backend using `boto3`.

### **Key behaviors**

- Connects to any S3-compatible endpoint:
  - AWS S3
  - MinIO
  - LocalStack
  - Cloudflare R2
- Creates bucket if missing.
- Uploads objects via `put_object`.
- Checks existence via `head_object`.

### **Why MinIO support matters**

MinIO allows:

- Local development with S3 semantics  
- Air‑gapped deployments  
- Enterprise S3-compatible storage  

This makes AILC‑SFTP cloud‑agnostic.

### **Example**

```python
storage = S3Storage(
    endpoint_url="http://localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket_name="ailc-bucket"
)
```

### **Current status**

The S3 adapter is implemented but not yet wired into the server by default.  
It becomes active when:

```
STORAGE_TYPE=S3
```

is set in `.env`.

---

## 5. How the SFTP Server Uses Storage

The server does **not** write files directly.

Instead:

- `AILCDiskInterface.open()` resolves the path.
- `LocalFileHandle` writes bytes to disk.
- On close, the server computes SHA‑256 and writes a sidecar.
- Storage adapters are used for:
  - saving files (future)
  - retrieving hashes
  - checking existence

This separation allows the SFTP protocol layer to remain stable while storage evolves.

---

## 6. Adding a New Storage Backend

To add a new backend:

### **Step 1 — Create a new file**
Example: `azure_storage.py`

### **Step 2 — Implement the interface**

```python
class AzureBlobStorage(BaseStorage):
    def save(self, file_name, data):
        # upload to Azure Blob
        return True

    def exists(self, file_name):
        # check blob existence
        return True

    def get_hash(self, file_name):
        # return blob SHA-256
        return "<hash>"
```

### **Step 3 — Add switch logic**

In `sftp_server.py`:

```python
if STORAGE_TYPE == "AZURE":
    storage = AzureBlobStorage(...)
```

### **Step 4 — Done**
No changes to:

- SFTP protocol  
- File handles  
- Integrity model  
- Client logic  

This is the power of the abstraction.

---

## 7. Future Storage Backends

Planned or easy-to-add backends:

- **Azure Blob Storage**  
- **Google Cloud Storage**  
- **NFS / SMB**  
- **Encrypted storage (AES‑GCM)**  
- **Versioned storage (Git‑like)**  
- **Immutable storage (WORM)**  

The architecture is intentionally small and flexible.

---

## 8. Summary

The storage adapter layer provides:

- clean decoupling  
- cloud-agnostic design  
- deterministic integrity support  
- AI-ready observability  
- easy extensibility  

This is the foundation that allows AILC‑SFTP to evolve from a local POC into a **portable, enterprise-grade, AI-observable file transfer engine**.


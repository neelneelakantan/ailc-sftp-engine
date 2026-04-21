import paramiko
import os
import hashlib
import uuid
from dotenv import load_dotenv
import time

from core.observability.logger import logger
from core.deterministic_layer.hasher import hash_file
from config.config import AILCConfig as CFG
from core.sftp_client.transfer_result import TransferResult

# Load variables
load_dotenv()
USER = os.getenv("SFTP_USER")
PASS = os.getenv("SFTP_PASS")
PORT = int(os.getenv("SFTP_PORT", 3373))

# Global Session ID for logging correlation
session_id = str(uuid.uuid4())


def get_file_hash(file_path):
    """Calculates SHA-256 of a local file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def resumable_upload(sftp, local_path, remote_name, chunk_size=100):
    """
    Uploads a file in chunks, optionally resuming from an existing remote file.
    Returns metrics needed for TransferResult.
    """
    chunks_sent = 0
    latency_profile = []
    total_bytes = 0

    local_size = os.path.getsize(local_path)
    remote_size = 0

    # Detect existing remote file
    try:
        remote_stat = sftp.stat(remote_name)
        remote_size = remote_stat.st_size
        if CFG.RESUMABLE_MODE and remote_size > 0:
            logger.info(f"🔍 Resumable mode: found partial file ({remote_size} bytes).")
        else:
            logger.info("ℹ️ Remote file exists but resumable mode disabled or empty.")
    except Exception:
        logger.info("ℹ️ No remote file found — starting fresh upload.")
        remote_size = 0

    mode = 'ab' if remote_size > 0 else 'wb'

    with sftp.open(remote_name, mode) as f_remote:
        with open(local_path, 'rb') as f_local:
            if remote_size > 0:
                f_local.seek(remote_size)

            while True:
                chunk = f_local.read(chunk_size)
                if not chunk:
                    break

                start = time.time()
                f_remote.write(chunk)
                latency_profile.append(int((time.time() - start) * 1000))

                chunks_sent += 1
                total_bytes += len(chunk)

                if CFG.CHUNK_SLEEP_MS > 0:
                    time.sleep(CFG.CHUNK_SLEEP_MS / 1000.0)

    return {
        "bytes_transferred": total_bytes,
        "chunks_sent": chunks_sent,
        "latency_profile": latency_profile
    }


def verify_transfer(sftp, local_path, remote_name):
    """Validates local vs remote manifest and actual remote bytes."""
    local_hash = get_file_hash(local_path)
    manifest_name = f"{remote_name}.sha256"
    remote_hash = ""

    # Wait for manifest
    for attempt in range(5):
        try:
            with sftp.open(manifest_name, "r") as f:
                remote_hash = f.read().decode('utf-8').strip()
            if remote_hash:
                break
        except Exception:
            pass

        time.sleep(CFG.MANIFEST_POLL_MS / 1000.0)

    # Compute actual remote hash
    with sftp.open(remote_name, "rb") as f:
        remote_bytes = f.read()
    remote_actual_hash = hashlib.sha256(remote_bytes).hexdigest()

    if local_hash != remote_actual_hash:
        logger.error(
            f"❌ Remote file bytes do NOT match local file! "
            f"Local: {local_hash[:8]} vs RemoteActual: {remote_actual_hash[:8]}",
            extra={"correlation_id": session_id}
        )
        return False

    if not remote_hash:
        logger.error(f"❌ Manifest empty or missing: {manifest_name}", extra={"correlation_id": session_id})
        return False

    if local_hash == remote_hash:
        logger.info(f"✅ INTEGRITY VERIFIED for {remote_name}", extra={"correlation_id": session_id})
        return True

    logger.error(
        f"❌ Hash Mismatch! Local: {local_hash[:8]} vs Remote: {remote_hash[:8]}",
        extra={"correlation_id": session_id}
    )
    return False


def secure_put(local_path: str, remote_name: str):
    """Main Orchestrator."""
    transport = paramiko.Transport(("127.0.0.1", PORT))

    retries = 0
    chunks_sent = 0
    latency_profile = []

    if not os.path.exists(local_path):
        return TransferResult(
            success=False,
            bytes_transferred=0,
            hash_match=False,
            error_log="Local file missing"
        )

    local_size = os.path.getsize(local_path)

    try:
        transport.connect(username=USER, password=PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Upload
        upload_metrics = resumable_upload(sftp, local_path, remote_name, chunk_size=CFG.CHUNK_SIZE)
        chunks_sent = upload_metrics["chunks_sent"]
        latency_profile = upload_metrics["latency_profile"]

        # Verify
        time.sleep(0.1)
        remote_stat = sftp.stat(remote_name)

        if remote_stat.st_size != local_size:
            time.sleep(0.2)
            remote_stat = sftp.stat(remote_name)

        hash_match = verify_transfer(sftp, local_path, remote_name)

        return TransferResult(
            success=hash_match,
            bytes_transferred=remote_stat.st_size,
            hash_match=hash_match,
            retries=retries,
            chunks_sent=chunks_sent,
            latency_profile_ms=latency_profile,
            local_file=local_path,
            remote_file=remote_name,
        )

    except Exception as e:
        return TransferResult(
            success=False,
            bytes_transferred=0,
            hash_match=False,
            error_log=str(e)
        )
    finally:
        transport.close()


if __name__ == "__main__":
    test_file = "test_payload.txt"
    result = secure_put(test_file, "remote_test.txt")
    logger.info(f"Final Result: {result}", extra={"correlation_id": session_id})

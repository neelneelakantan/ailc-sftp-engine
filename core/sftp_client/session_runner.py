import json
import time
import uuid
from datetime import datetime

from .sftp_agent import secure_put
from .connection import get_sftp_client   # whatever your connect helper is


def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def run_session(local_path: str, remote_name: str = "remote_test.txt"):
    session_id = str(uuid.uuid4())
    start_time = time.time()
    start_ts = now_iso()

    if remote_name is None:
        remote_name = local_path.split("/")[-1]

    print(f"[session {session_id}] starting upload")
    print(f"[session {session_id}] local={local_path} remote={remote_name}")

    try:
        sftp = get_sftp_client()
    except Exception as e:
        return {
            "session_id": session_id,
            "start_time": start_ts,
            "end_time": now_iso(),
            "success": False,
            "error": "ConnectionFailed",
            "details": str(e),
        }

    try:
        result = secure_put(local_path, remote_name)
    except Exception as e:
        return {
            "session_id": session_id,
            "start_time": start_ts,
            "end_time": now_iso(),
            "success": False,
            "error": "UploadFailed",
            "details": str(e),
        }
    finally:
        try:
            sftp.close()
        except:
            pass

    end_ts = now_iso()
    duration_ms = int((time.time() - start_time) * 1000)

    # secure_put already returns a TransferResult dataclass
    return {
        "session_id": session_id,
        "start_time": start_ts,
        "end_time": end_ts,
        "duration_ms": duration_ms,
        "local_file": local_path,
        "remote_file": remote_name,
        "bytes_transferred": result.bytes_transferred,
        "hash_match": result.hash_match,
        "success": result.success,
        "retries": result.retries,
        "chunks_sent": result.chunks_sent,
        "latency_profile_ms": result.latency_profile_ms,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m core.sftp_client.session_runner <local_file>")
        sys.exit(1)

    local_path = sys.argv[1]
    output = run_session(local_path)
    print(json.dumps(output, indent=2))


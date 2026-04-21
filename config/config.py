import os

def _bool(value, default=False):
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes", "on")

class AILCConfig:
    # Resumable upload mode (off by default for safety)
    RESUMABLE_MODE = _bool(os.getenv("RESUMABLE_MODE"), default=False)

    # Chunk size for resumable upload (bytes)
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1024"))

    # Sleep between chunks (ms) for simulation
    CHUNK_SLEEP_MS = int(os.getenv("CHUNK_SLEEP_MS", "0"))

    # Manifest wait timeout (ms)
    MANIFEST_WAIT_MS = int(os.getenv("MANIFEST_WAIT_MS", "2000"))

    # Poll interval for manifest (ms)
    MANIFEST_POLL_MS = int(os.getenv("MANIFEST_POLL_MS", "200"))

    # Verbose logging
    VERBOSE = _bool(os.getenv("VERBOSE"), default=True)

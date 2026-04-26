from dataclasses import dataclass, field
from typing import List


@dataclass
class TransferResult:
    success: bool
    bytes_transferred: int
    hash_match: bool
    retries: int = 0
    chunks_sent: int = 0
    latency_profile_ms: List[int] = field(default_factory=list)

    # Optional: include remote/local names if you want richer JSON
    local_file: str = ""
    remote_file: str = ""
    error_log: str = ""



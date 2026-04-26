from dataclasses import dataclass

@dataclass
class ChunkObservation:
    latency_ms: int
    chunk_size: int
    chunk_index: int
    bytes_sent: int
    offset: int


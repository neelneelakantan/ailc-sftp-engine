from dataclasses import dataclass

@dataclass
class ChunkAction:
    decision: str          # 'grow', 'shrink', 'keep', or 'blend(...)'
    old_size: int
    new_size: int
    confidence: float

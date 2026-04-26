from core.sftp_client.action import ChunkAction
from core.sftp_client.policy import ChunkSizePolicy
from core.sftp_client.strategy_selector import StrategySelector

class AdaptiveChunkController:

    def __init__(self, initial_size, min_size=256, max_size=4096):
        self.chunk_size = initial_size
        self.min_size = min_size
        self.max_size = max_size
        self.policy = ChunkSizePolicy()
        self.selector = StrategySelector()

    def apply_decision(self, obs, decision, confidence):
        old = self.chunk_size

        strategy = self.selector.choose(confidence)
        self.chunk_size = strategy.scale(
            current_size=self.chunk_size,
            min_size=self.min_size,
            max_size=self.max_size,
            decision=decision,
        )

        return ChunkAction(
            decision=decision,
            old_size=old,
            new_size=self.chunk_size,
            confidence=confidence,
        )


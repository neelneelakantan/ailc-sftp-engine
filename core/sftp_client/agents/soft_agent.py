from core.sftp_client.action import ChunkAction

class SoftAgent:
    """
    Advisory agent: suggests overrides, but expects the controller
    to decide whether to accept them.
    """
    def adjust(self, obs, memory, decision, confidence):
        # High confidence → don't interfere
        if confidence >= 0.8:
            print(f"[agent] High confidence ({confidence:.2f}), no override", flush=True)
            return None

        # Example: if latency is noisy but below threshold, be conservative
        if 5 <= obs.latency_ms <= 50 and decision == "grow":
            return ChunkAction(
                decision="keep",
                old_size=obs.chunk_size,
                new_size=obs.chunk_size,
                confidence=confidence * 0.9,
            )

        # Otherwise, no override
        return None

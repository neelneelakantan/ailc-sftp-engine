class ChunkSizePolicy:
    """
    Deterministic reasoning policy.
    Later, an agentic policy can replace this one.
    """
    def decide(self, obs):
        """
        Returns one of: 'shrink', 'grow', or 'keep'
        """
        if obs.latency_ms > 50:
            return "shrink"
        elif obs.latency_ms < 5:
            return "grow"
        else:
            return "keep"

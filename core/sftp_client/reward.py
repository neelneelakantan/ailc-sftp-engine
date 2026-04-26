class RewardSignal:
    """
    Deterministic reward based on change in latency.
    Positive = improvement, negative = degradation.
    """

    def compute(self, prev_obs, curr_obs):
        if prev_obs is None:
            return 0.0

        # Lower latency is better
        delta = prev_obs.latency_ms - curr_obs.latency_ms

        # Normalize a bit
        return max(-1.0, min(1.0, delta / 50.0))

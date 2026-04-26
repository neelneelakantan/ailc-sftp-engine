class LearningWeightAdjuster:
    """
    Deterministic adaptive weight adjuster.
    Adjusts agent trust based on stability of recent actions.
    """

    def __init__(self, initial_weight=0.0, min_w=0.0, max_w=1.0):
        self.weight = initial_weight
        self.min_w = min_w
        self.max_w = max_w

    def update(self, memory, avg_reward):
        # Need at least 3 samples to detect stability
        if len(memory.history) < 3:
            return self.weight

        last_sizes = [a.new_size for (o, a) in memory.history[-3:]]

        stable = last_sizes[0] == last_sizes[1] == last_sizes[2]
        oscillating = (
            last_sizes[0] < last_sizes[1] > last_sizes[2] or
            last_sizes[0] > last_sizes[1] < last_sizes[2]
        )

        if stable:
            # System is stable → trust agent a bit more
            self.weight = min(self.max_w, self.weight + 0.05)

        if oscillating:
            # System is unstable → trust agent less
            self.weight = max(self.min_w, self.weight - 0.1)

        return self.weight


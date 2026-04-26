# core/sftp_client/performance.py

class PerformanceEvaluator:
    """
    Tracks rolling reward to guide adaptive weighting.
    """

    def __init__(self, window=5):
        self.window = window
        self.rewards = []

    def update(self, reward: float):
        self.rewards.append(reward)
        if len(self.rewards) > self.window:
            self.rewards.pop(0)

    def average(self) -> float:
        if not self.rewards:
            return 0.0
        return sum(self.rewards) / len(self.rewards)



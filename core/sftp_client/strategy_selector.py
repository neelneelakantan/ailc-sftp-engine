from core.sftp_client.strategy import BaseStrategy, ConservativeStrategy, AggressiveStrategy

class StrategySelector:
    def __init__(self):
        self.base = BaseStrategy()
        self.conservative = ConservativeStrategy()
        self.aggressive = AggressiveStrategy()

    def choose(self, confidence):
        if confidence < 0.3:
            return self.conservative
        elif confidence > 0.7:
            return self.aggressive
        return self.base


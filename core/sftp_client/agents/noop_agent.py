
class NoOpAgent:
    """
    First agent in the system.
    Observes everything, overrides nothing.
    """
    def adjust(self, obs, memory, decision, confidence):
        # Could log, analyze, or store elsewhere
        return None  # No override


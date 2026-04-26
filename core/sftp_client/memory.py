
class ChunkMemory:
    """
    Placeholder for agentic learning.
    Stores recent observations and actions.
    """
    def __init__(self, max_history=20):
        self.history = []
        self.max_history = max_history

    def record(self, obs, action):
        self.history.append((obs, action))
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def last(self):
        return self.history[-1] if self.history else None

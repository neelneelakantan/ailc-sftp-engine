
class BaseStrategy:
    def scale(self, current_size, min_size, max_size, decision):
        if decision == "shrink":
            return max(min_size, current_size // 2)
        elif decision == "grow":
            return min(max_size, current_size * 2)
        return current_size


class ConservativeStrategy(BaseStrategy):
    def scale(self, current_size, min_size, max_size, decision):
        # Only shrink aggressively; grow more cautiously
        if decision == "shrink":
            return max(min_size, current_size // 2)
        elif decision == "grow":
            return min(max_size, current_size + 256)
        return current_size


class AggressiveStrategy(BaseStrategy):
    def scale(self, current_size, min_size, max_size, decision):
        # Grow faster when asked to grow
        if decision == "shrink":
            return max(min_size, current_size // 2)
        elif decision == "grow":
            return min(max_size, current_size * 2)
        return current_size

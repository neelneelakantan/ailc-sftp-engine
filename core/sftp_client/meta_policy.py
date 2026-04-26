

class MetaPolicy:
    def __init__(self, base_policy):
        self.base = base_policy

    def decide(self, obs, memory):
        decision = self.base.decide(obs)

        if len(memory.history) < 3:
            return decision, 0.5  # neutral confidence

        last_latencies = [o.latency_ms for (o, a) in memory.history[-3:]]

        increasing = last_latencies[0] < last_latencies[1] < last_latencies[2]
        decreasing = last_latencies[0] > last_latencies[1] > last_latencies[2]

        # Trend confidence
        if increasing or decreasing:
            trend_conf = 0.8
        else:
            trend_conf = 0.4

        # Distance from thresholds
        if obs.latency_ms > 50:
            dist_conf = min(1.0, (obs.latency_ms - 50) / 50)
        elif obs.latency_ms < 5:
            dist_conf = min(1.0, (5 - obs.latency_ms) / 5)
        else:
            dist_conf = 0.3

        # Combine
        confidence = (trend_conf + dist_conf) / 2
        return decision, confidence


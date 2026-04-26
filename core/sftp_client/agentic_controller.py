
from core.sftp_client.action import ChunkAction
from core.sftp_client.memory import ChunkMemory
from core.sftp_client.meta_policy import MetaPolicy
from core.sftp_client.learning_weight import LearningWeightAdjuster
from core.sftp_client.performance import PerformanceEvaluator
from core.sftp_client.reward import RewardSignal


class AgenticController:
    """
    Wrapper that can switch between deterministic and agentic policies.
    For now, it simply delegates to the deterministic controller.
    """
    def __init__(
        self,
        deterministic_controller,
        comparison_mode=False,
        conditional_override=False,
        full_override=True,
        blend_mode=False
    ):
        self.det = deterministic_controller
        self.agent = None
        self.memory = ChunkMemory()
        self.meta = MetaPolicy(self.det.policy)
        self.comparison_mode = comparison_mode
        self.conditional_override = conditional_override
        self.full_override = full_override
        self.blend_mode = blend_mode
        self.weight_adjuster = LearningWeightAdjuster()
        self.reward = RewardSignal()
        self.performance = PerformanceEvaluator()

    def adjust(self, obs):
        # Step 1: meta-policy decides
        decision, confidence = self.meta.decide(obs, self.memory)

        # Step 2: deterministic action
        det_action = self.det.apply_decision(obs, decision, confidence)

        # Step 3: agent suggestion
        agent_action = None
        if self.agent:
            print(f"[meta] decision={decision} conf={confidence:.2f}")
            agent_action = self.agent.adjust(
                obs=obs,
                memory=self.memory,
                decision=decision,
                confidence=confidence
            )

        # Step 4: comparison mode (shadow)
        if self.comparison_mode and agent_action:
            self._log_divergence(det_action, agent_action)

        # Step 5: conditional override
        if self.conditional_override and agent_action and confidence < 0.3:
            action = agent_action
        else:
            action = det_action

        # Step 6: blend mode
        if self.blend_mode and agent_action:
            action = self._blend_actions(det_action, agent_action, confidence)

        # Step 7: full override mode
        if self.full_override and agent_action:
            action = agent_action

        # Step 8: record memory
        self.memory.record(obs, action)

        # ---- FIXED ORDER BELOW ----

        # Step 9: compute reward
        prev = self.memory.history[-2][0] if len(self.memory.history) >= 2 else None
        r = self.reward.compute(prev, obs)
        print(f"[reward] r={r:.2f}")

        # Step 10: update performance window
        self.performance.update(r)
        avg_r = self.performance.average()
        print(f"[perf] avg_reward={avg_r:.2f}")

        # Step 11: update learning weight (now avg_r is defined)
        new_weight = self.weight_adjuster.update(self.memory, avg_r)
        print(f"[learning] agent_weight={new_weight:.2f}")

        # Step 12: return final action
        return action



    def _log_divergence(self, det_action, agent_action):
        if det_action.new_size != agent_action.new_size:
            print(
                f"[comparison] det={det_action.new_size} "
                f"agent={agent_action.new_size} "
                f"decision={agent_action.decision} "
                f"conf={agent_action.confidence:.2f}"
            )

            print(
                f"Force: [comparison] det={det_action.new_size} "
                f"agent={agent_action.new_size} "
                f"decision={agent_action.decision} "
                f"conf={agent_action.confidence:.2f}"
            )


    def _blend_actions(self, det_action, agent_action, confidence):
        learned_weight = self.weight_adjuster.weight
        
        # Combine learned weight with confidence-based weight
        weight_agent = max(0.0, learned_weight * (1.0 - confidence))
        weight_det = 1.0 - weight_agent
        
        blended_size = int(
            det_action.new_size * weight_det +
            agent_action.new_size * weight_agent
        )

        return ChunkAction(
            decision=f"blend({det_action.decision},{agent_action.decision})",
            old_size=det_action.old_size,
            new_size=blended_size,
            confidence=confidence
        )

    @property
    def chunk_size(self):
        return self.det.chunk_size

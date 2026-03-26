from typing import Any, Dict, Optional, Tuple
from app.models import Action, Observation, Reward, VALID_ACTION_TYPES
from app.tasks import get_task, TASKS
from app.rewards import compute_reward

MAX_STEPS = 5


class ContractRiskEnv:
    def __init__(self) -> None:
        self._current_task_name: str = "easy"
        self._task: Dict[str, Any] = get_task("easy")
        self._observation: Observation = self._make_initial_observation()
        self._step_count: int = 0
        self._done: bool = False

    def _make_initial_observation(self) -> Observation:
        return Observation(
            email=self._task["email"],
            contract_clause=self._task["contract_clause"],
            detected_risk=None,
            risk_type=None,
            proposed_fix=None,
            history=[],
            task_description=self._task["task_description"],
        )

    def reset(self, task_name: Optional[str] = None) -> Dict[str, Any]:
        if task_name is not None:
            if task_name not in TASKS:
                raise ValueError(f"Unknown task '{task_name}'. Available: {list(TASKS.keys())}")
            self._current_task_name = task_name

        self._task = get_task(self._current_task_name)
        self._observation = self._make_initial_observation()
        self._step_count = 0
        self._done = False

        return self._observation.model_dump()

    def step(self, action_data: Dict[str, Any]) -> Tuple[Dict, float, bool, Dict]:
        if self._done:
            return self._observation.model_dump(), 0.0, True, {
                "error": "Episode already done. Call reset()."
            }

        is_invalid = False
        action_type = action_data.get("action_type", "")
        content = action_data.get("content", "")

        # Validate action type
        if action_type not in VALID_ACTION_TYPES:
            is_invalid = True
            self._observation.history.append(
                f"[INVALID ACTION] '{action_type}' is not valid"
            )
        else:
            # Apply action with logical constraints
            was_applied = self._apply_action(action_type, content)
            if not was_applied:
                is_invalid = True

        self._step_count += 1

        # Compute reward
        reward_value = compute_reward(
            task=self._task,
            observation=self._observation.model_dump(),
            action_type=action_type,
            content=content,
            is_invalid_action=is_invalid,
            step_count=self._step_count,
        )

        # Check completion
        all_filled = (
            self._observation.detected_risk is not None
            and self._observation.risk_type is not None
            and self._observation.proposed_fix is not None
            and any("send_reply" in h.lower() for h in self._observation.history)
        )

        if all_filled or self._step_count >= MAX_STEPS:
            self._done = True

        info = {
            "step": self._step_count,
            "max_steps": MAX_STEPS,
            "task": self._current_task_name,
            "is_invalid_action": is_invalid,
        }

        reward = Reward(
            score=reward_value,
            breakdown={
                "step_count": self._step_count,
                "detected_risk": self._observation.detected_risk,
                "risk_type": self._observation.risk_type,
                "proposed_fix": self._observation.proposed_fix,
                "is_invalid_action": is_invalid,
            },
        )

        return self._observation.model_dump(), reward.score, self._done, info

    def _apply_action(self, action_type: str, content: str) -> bool:
        """
        Returns True if action applied successfully, False if invalid (logic violation)
        """

        # 🚨 Enforce logical order
        if action_type == "classify_risk_type" and not self._observation.detected_risk:
            self._observation.history.append("[INVALID] must identify risk first")
            return False

        if action_type == "propose_fix" and not self._observation.detected_risk:
            self._observation.history.append("[INVALID] must identify risk before fix")
            return False

        if action_type == "send_reply" and not self._observation.proposed_fix:
            self._observation.history.append("[INVALID] must propose fix before reply")
            return False

        # 🚨 Prevent repeated reply spam
        if action_type == "send_reply":
            if any("send_reply" in h.lower() for h in self._observation.history):
                self._observation.history.append("[INVALID] multiple replies not allowed")
                return False

        # ✅ Apply valid action
        if action_type == "identify_risk":
            self._observation.detected_risk = content
            self._observation.history.append(f"[identify_risk] {content}")

        elif action_type == "classify_risk_type":
            self._observation.risk_type = content
            self._observation.history.append(f"[classify_risk_type] {content}")

        elif action_type == "propose_fix":
            self._observation.proposed_fix = content
            self._observation.history.append(f"[propose_fix] {content}")

        elif action_type == "send_reply":
            self._observation.history.append(f"[send_reply] {content}")

        return True

    def state(self) -> Dict[str, Any]:
        return {
            "task": self._current_task_name,
            "step": self._step_count,
            "max_steps": MAX_STEPS,
            "done": self._done,
            "observation": self._observation.model_dump(),
        }
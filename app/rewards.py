from typing import Any, Dict


def compute_reward(
    task: Dict[str, Any],
    observation: Dict[str, Any],
    action_type: str,
    content: str,
    is_invalid_action: bool,
    step_count: int,
) -> float:
    score = 0.0

    if is_invalid_action:
        score -= 0.2
        score -= 0.05 * step_count
        return max(0.0, min(1.0, score))

    difficulty = task.get("difficulty", "easy")
    detected_risk = (observation.get("detected_risk") or "").lower()
    risk_type = (observation.get("risk_type") or "").lower()
    proposed_fix = (observation.get("proposed_fix") or "").lower()
    reply = ""
    history = observation.get("history", [])
    for entry in history:
        if "send_reply" in entry.lower():
            reply = entry.lower()
            break

    expected_risk = (task.get("expected_risk") or "").lower()
    expected_type = (task.get("expected_risk_type") or "").lower()
    fix_keywords = task.get("expected_fix_keywords", [])
    reply_keywords = task.get("expected_reply_keywords", [])

    if expected_risk and any(word in detected_risk for word in expected_risk.split()):
        score += 0.3

    if expected_type and expected_type in risk_type:
        score += 0.3

    if fix_keywords and any(kw in proposed_fix for kw in fix_keywords):
        score += 0.3

    if reply_keywords and any(kw in reply for kw in reply_keywords):
        score += 0.1

    score -= 0.05 * step_count

    return max(0.0, min(1.0, score))

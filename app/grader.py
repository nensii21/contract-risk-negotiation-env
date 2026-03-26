from typing import Any, Dict


def grade(task: Dict[str, Any], observation: Dict[str, Any]) -> float:
    difficulty = task.get("difficulty", "easy")

    detected_risk = (observation.get("detected_risk") or "").lower()
    risk_type = (observation.get("risk_type") or "").lower()
    proposed_fix = (observation.get("proposed_fix") or "").lower()

    history = observation.get("history", [])
    reply = ""

    # Extract reply
    for entry in history:
        if "send_reply" in entry.lower():
            reply = entry.lower()
            break

    # ---------------- EASY ----------------
    if difficulty == "easy":
        expected = (task.get("expected_risk") or "").lower()
        if expected and expected in detected_risk:
            return 1.0
        return 0.0

    # ---------------- MEDIUM ----------------
    elif difficulty == "medium":
        score = 0.0

        expected_risk = (task.get("expected_risk") or "").lower()
        expected_type = (task.get("expected_risk_type") or "").lower()

        if expected_risk and expected_risk in detected_risk:
            score += 0.5

        if expected_type and expected_type in risk_type:
            score += 0.5
        elif risk_type:
            score += 0.2  # partial credit

        return max(0.0, min(1.0, score))

    # ---------------- HARD ----------------
    elif difficulty == "hard":
        score = 0.0
        expected_risk = (task.get("expected_risk") or "").lower()

        # Risk detection
        if expected_risk and expected_risk in detected_risk:
            score += 0.3
        elif detected_risk:
            score += 0.1

        # Fix scoring
        if "termination" in proposed_fix:
            score += 0.1
        if "allow" in proposed_fix or "modify" in proposed_fix:
            score += 0.1
        if "notice" in proposed_fix:
            score += 0.1

        # Reply scoring
        if "please" in reply:
            score += 0.1
        if "suggest" in reply or "recommend" in reply:
            score += 0.15
        if "because" in reply or "due to" in reply:
            score += 0.15

        return max(0.0, min(1.0, score))

    return 0.0
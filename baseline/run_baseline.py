import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.env import ContractRiskEnv
from app.tasks import get_task, TASKS
from app.grader import grade


def run_task(task_name: str) -> float:
    env = ContractRiskEnv()
    obs = env.reset(task_name=task_name)
    task = get_task(task_name)

    print(f"\n{'='*60}")
    print(f"Task: {task_name.upper()} ({task['difficulty']})")
    print(f"Email: {obs['email']}")
    print(f"Clause: {obs['contract_clause']}")
    print(f"{'='*60}")

    for step_num in range(1, 6):
        current_state = env.state()
        obs = current_state["observation"]

        clause = obs["contract_clause"].lower()

        # ---------- STEP 1: IDENTIFY RISK ----------
        if not obs["detected_risk"]:
            if "liability" in clause:
                content = "unlimited liability"
            elif "renew" in clause:
                content = "auto renewal risk"
            elif "termination" in clause:
                content = "termination restriction"
            else:
                content = "contract risk"

            action_data = {
                "action_type": "identify_risk",
                "content": content
            }

        # ---------- STEP 2: CLASSIFY (ONLY FOR MEDIUM/HARD) ----------
        elif not obs["risk_type"] and task_name != "easy":
            action_data = {
                "action_type": "classify_risk_type",
                "content": "legal"
            }

        # ---------- STEP 3: PROPOSE FIX ----------
        elif not obs["proposed_fix"]:
            if "termination" in clause:
                fix = "suggest allowing termination with prior notice"
            elif "renew" in clause:
                fix = "suggest adding notice before auto renewal"
            else:
                fix = "suggest limiting liability to a reasonable amount"

            action_data = {
                "action_type": "propose_fix",
                "content": fix
            }

        # ---------- STEP 4: SEND REPLY ----------
        elif not any("send_reply" in h.lower() for h in obs["history"]):
            action_data = {
                "action_type": "send_reply",
                "content": "Please consider revising the clause. I suggest modifying it to reduce risk and ensure fairness."
            }

        # ---------- STOP ----------
        else:
            break

        obs_new, reward, done, info = env.step(action_data)

        print(f"  Step {step_num}: action={action_data['action_type']}, reward={reward:.3f}")

        if done:
            break

    final_obs = env.state()["observation"]
    score = grade(task=task, observation=final_obs)

    print(f"  Final Score: {score:.3f}")
    return score


def main():
    all_scores = {}

    for task_name in TASKS.keys():
        score = run_task(task_name)
        all_scores[task_name] = score

    print(f"\n{'='*60}")
    print("BASELINE RESULTS")
    print(f"{'='*60}")

    for task_name, score in all_scores.items():
        print(f"  {task_name}: {score:.3f}")

    print(f"  Average: {sum(all_scores.values()) / len(all_scores):.3f}")


if __name__ == "__main__":
    main()
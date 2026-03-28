from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
from pydantic import BaseModel, ValidationError

from app.env import ContractRiskEnv
from app.tasks import list_tasks, get_task
from app.grader import grade

app = FastAPI(
    title="contract-risk-negotiation-env",
    description="OpenEnv environment for contract risk identification and negotiation",
    version="1.0.0",
)

env = ContractRiskEnv()


class StepRequest(BaseModel):
    action_type: str
    content: str


class ResetRequest(BaseModel):
    task_name: Optional[str] = None


@app.get("/reset")
def reset(task_name: Optional[str] = None) -> Dict[str, Any]:
    try:
        observation = env.reset(task_name=task_name)
        return {"observation": observation}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(request: StepRequest) -> Dict[str, Any]:
    action_data = {"action_type": request.action_type, "content": request.content}
    observation, reward, done, info = env.step(action_data)
    return {
        "observation": observation,
        "reward": reward,
        "done": done,
        "info": info,
    }


@app.get("/state")
def state() -> Dict[str, Any]:
    return env.state()




@app.get("/grader")
def grader() -> Dict[str, Any]:
    current_state = env.state()
    task_name = current_state["task"]
    task = get_task(task_name)
    observation = current_state["observation"]
    score = grade(task=task, observation=observation)
    return {
        "task": task_name,
        "score": score,
        "observation": observation,
    }


@app.get("/baseline")
def baseline() -> Dict[str, Any]:
    from app.tasks import TASKS

    results = {}
    for task_name, task_def in TASKS.items():
        env_tmp = ContractRiskEnv()
        env_tmp.reset(task_name=task_name)

        task = get_task(task_name)
        difficulty = task["difficulty"]

        actions = _get_baseline_actions(task_name, task_def)
        for action in actions:
            obs, reward, done, info = env_tmp.step(action)
            if done:
                break

        final_obs = env_tmp.state()["observation"]
        score = grade(task=task, observation=final_obs)
        results[task_name] = {
            "difficulty": difficulty,
            "score": score,
            "observation": final_obs,
        }

    return {"baseline_results": results}


def _get_baseline_actions(task_name: str, task_def: Dict[str, Any]):
    clause = task_def["contract_clause"].lower()

    if task_name == "easy":
        return [
            {"action_type": "identify_risk", "content": "unlimited liability"},
        ]
    elif task_name == "medium":
        return [
            {"action_type": "identify_risk", "content": "auto renewal"},
            {"action_type": "classify_risk_type", "content": "financial"},
        ]
    elif task_name == "hard":
        return [
            {"action_type": "identify_risk", "content": "no termination clause detected"},
            {"action_type": "classify_risk_type", "content": "legal"},
            {
                "action_type": "propose_fix",
                "content": (
                    "We recommend adding a clause to limit the scope of the restriction and allow "
                    "either party to terminate the agreement with 30 days written notice. "
                    "The current clause should be modified to include standard exit provisions."
                ),
            },
            {
                "action_type": "send_reply",
                "content": (
                    "Dear Team, thank you for sending the contract. We have reviewed the terms and "
                    "would like to suggest revisions to the termination clause. We recommend including "
                    "exit provisions to allow either party to terminate with prior notice. "
                    "Please review our proposed modifications and let us know if you have any questions."
                ),
            },
        ]
    return []

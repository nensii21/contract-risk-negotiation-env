from typing import List, Optional
from pydantic import BaseModel, field_validator

VALID_ACTION_TYPES = {
    "identify_risk",
    "classify_risk_type",
    "propose_fix",
    "send_reply",
}


class Observation(BaseModel):
    email: str
    contract_clause: str
    detected_risk: Optional[str] = None
    risk_type: Optional[str] = None
    proposed_fix: Optional[str] = None
    history: List[str] = []
    task_description: str


class Action(BaseModel):
    action_type: str
    content: str

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, v: str) -> str:
        if v not in VALID_ACTION_TYPES:
            raise ValueError(
                f"Invalid action_type '{v}'. Must be one of: {sorted(VALID_ACTION_TYPES)}"
            )
        return v


class Reward(BaseModel):
    score: float
    breakdown: dict

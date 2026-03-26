from typing import Dict, Any

TASKS: Dict[str, Dict[str, Any]] = {
    "easy": {
        "name": "easy",
        "difficulty": "easy",
        "email": "Dear Vendor, please review the attached contract and let us know if you agree to the terms.",
        "contract_clause": "Vendor has unlimited liability",
        "task_description": (
            "EASY TASK: You are a contract risk analyst. Read the email and contract clause. "
            "Identify any risks present in the contract clause. "
            "Expected: detect 'unlimited liability' as the risk."
        ),
        "expected_risk": "unlimited liability",
        "expected_risk_type": None,
        "expected_fix_keywords": [],
        "expected_reply_keywords": [],
    },
    "medium": {
        "name": "medium",
        "difficulty": "medium",
        "email": "Hello, we would like you to review the auto-renewal clause in our standard agreement.",
        "contract_clause": "Contract auto-renews without notice",
        "task_description": (
            "MEDIUM TASK: You are a contract risk analyst. Read the email and contract clause. "
            "Identify the risk and classify its type. "
            "Expected: detect 'auto renewal' as the risk and classify type as 'financial'."
        ),
        "expected_risk": "auto renewal",
        "expected_risk_type": "financial",
        "expected_fix_keywords": [],
        "expected_reply_keywords": [],
    },
    "hard": {
        "name": "hard",
        "difficulty": "hard",
        "email": "Please sign this quickly",
        "contract_clause": "No termination allowed",
        "task_description": (
            "HARD TASK: You are a contract risk analyst. Read the urgent email and the restrictive contract clause. "
            "Identify the risk, propose a fix (must include keywords: limit, terminate, or modify), "
            "and send a professional reply (must include: please, suggest, or recommend). "
            "Expected: detect termination risk, propose a fix with limit/terminate/modify, reply with polite tone."
        ),
        "expected_risk": "no termination",
        "expected_risk_type": None,
        "expected_fix_keywords": ["limit", "terminate", "modify"],
        "expected_reply_keywords": ["please", "suggest", "recommend"],
    },
}


def get_task(name: str) -> Dict[str, Any]:
    if name not in TASKS:
        raise ValueError(f"Unknown task '{name}'. Available: {list(TASKS.keys())}")
    return TASKS[name]


def list_tasks() -> Dict[str, Dict[str, Any]]:
    return {
        k: {
            "name": v["name"],
            "difficulty": v["difficulty"],
            "email": v["email"],
            "contract_clause": v["contract_clause"],
            "task_description": v["task_description"],
        }
        for k, v in TASKS.items()
    }

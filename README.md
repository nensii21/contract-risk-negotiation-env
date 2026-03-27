---
title: Contract Risk Env
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---
# contract-risk-negotiation-env

## Environment Description

`contract-risk-negotiation-env` is an OpenEnv-compatible reinforcement learning environment that simulates a real-world contract risk analysis workflow. An AI agent reads an incoming email and a contract clause, then must:

1. **Identify** the risk present in the contract clause
2. **Classify** the type of risk (e.g., financial, legal)
3. **Propose** a fix or amendment
4. **Send** a professional reply to the email

## Real-World Motivation

Contract review is a critical but time-consuming task in business and legal operations. Automated agents that can read contract language, flag risky clauses, propose remediation, and draft professional responses reduce legal exposure and accelerate deal cycles. This environment benchmarks and trains agents to perform these tasks accurately.

## Action Definitions

| Action | Description |
|---|---|
| `identify_risk` | Identify and describe the main risk in the contract clause |
| `classify_risk_type` | Classify the type of risk (financial, legal, operational, etc.) |
| `propose_fix` | Propose a specific fix or amendment to the clause |
| `send_reply` | Send a professional email reply to the original sender |

## Observation Fields

| Field | Type | Description |
|---|---|---|
| `email` | str | The incoming email to the analyst |
| `contract_clause` | str | The contract clause to review |
| `detected_risk` | str \| null | Identified risk (filled after `identify_risk`) |
| `risk_type` | str \| null | Risk classification (filled after `classify_risk_type`) |
| `proposed_fix` | str \| null | Proposed fix (filled after `propose_fix`) |
| `history` | list[str] | Chronological action history |
| `task_description` | str | Natural language task instructions |

## Task Descriptions

### Easy
- **Clause**: "Vendor has unlimited liability"
- **Goal**: Detect `unlimited liability` as the risk
- **Scoring**: Correct detection → 1.0

### Medium
- **Clause**: "Contract auto-renews without notice"
- **Goal**: Detect `auto renewal` and classify type as `financial`
- **Scoring**: Detection = 0.5, classification = 0.5

### Hard
- **Email**: "Please sign this quickly"
- **Clause**: "No termination allowed"
- **Goal**: Detect risk + propose fix (keywords: limit/terminate/modify) + polite reply (please/suggest/recommend)
- **Scoring**: Detection = 0.3, fix = 0.3, reply tone = 0.4

## Reward Function

| Event | Reward |
|---|---|
| Correct risk detection | +0.3 |
| Correct risk classification | +0.3 |
| Valid fix proposed | +0.3 |
| Good professional reply | +0.1 |
| Per step penalty | -0.05 |
| Invalid action | -0.2 |
| Final score clamped to | [0.0, 1.0] |

## Setup Instructions

### Local (Python 3.12)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.server:app --host 0.0.0.0 --port 7860
```

### Docker (Python 3.10)

```bash
# Build the image
docker build -t contract-risk-env .

# Run the container
docker run -p 7860:7860 contract-risk-env
```

### Baseline Script (requires OpenAI API key)

```bash
export OPENAI_API_KEY=your_key_here
python baseline/run_baseline.py
```

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/reset` | GET | Reset environment (optional `?task_name=easy\|medium\|hard`) |
| `/step` | POST | Take an action, get observation+reward |
| `/state` | GET | Get current environment state |
| `/tasks` | GET | List all available tasks |
| `/grader` | GET | Get deterministic score for current state |
| `/baseline` | GET | Run rule-based baseline on all tasks |

## Example API Calls

### Reset to a task
```bash
curl "http://localhost:7860/reset?task_name=easy"
```

### Take a step
```bash
curl -X POST "http://localhost:7860/step" \
  -H "Content-Type: application/json" \
  -d '{"action_type": "identify_risk", "content": "unlimited liability"}'
```

### Get current state
```bash
curl "http://localhost:7860/state"
```

### Get grader score
```bash
curl "http://localhost:7860/grader"
```

### List tasks
```bash
curl "http://localhost:7860/tasks"
```

### Run baseline
```bash
curl "http://localhost:7860/baseline"
```

### Step response format
```json
{
  "observation": {
    "email": "...",
    "contract_clause": "...",
    "detected_risk": "unlimited liability",
    "risk_type": null,
    "proposed_fix": null,
    "history": ["[identify_risk] unlimited liability"],
    "task_description": "..."
  },
  "reward": 0.25,
  "done": false,
  "info": {
    "step": 1,
    "max_steps": 5,
    "task": "easy",
    "is_invalid_action": false
  }
}
```

## Baseline Scores

Expected deterministic baseline scores (rule-based agent):

| Task | Difficulty | Expected Score |
|---|---|---|
| easy | Easy | 1.0 |
| medium | Medium | 0.9 |
| hard | Hard | 1.0 |

> Actual LLM baseline scores will vary based on model quality and prompting.

# API Request & Response Payload Examples

## 1. POST `/analyze`

### Request Payload
```json
{
  "ticker": "RELIANCE.NSE",
  "investment_horizon_days": 365
}
```

### Response Payload (200 OK)
```json
{
  "ticker": "RELIANCE.NSE",
  "recommendation": "BUY",
  "consensus_score": 0.82,
  "risk_level": "MODERATE",
  "is_suitable_for_portfolio": true,
  "reasoning_summary": "Strong fundamental balance sheet and revenue growth.",
  "analyzed_at": "2026-07-24T18:30:00Z"
}
```

---

## 2. POST `/committee/evaluate`

### Request Payload
```json
{
  "ticker": "INFY.NSE",
  "horizon": "LONG_TERM",
  "style": "VALUE",
  "user_query": "Evaluate long-term investment thesis."
}
```

### Response Payload (200 OK)
```json
{
  "decision_id": "dec-9a8b7c6d",
  "session_id": "f3a78305-88f5-4c76-8f74-2be1dce8506c",
  "ticker": "INFY.NSE",
  "winning_recommendation": "BUY",
  "consensus_score": 0.85,
  "confidence": 0.88,
  "agreement_ratio": 1.0,
  "verdict_summary": "Committee Judgement: Confidence=0.88, EvidenceStrength=0.9, Quality=0.95.",
  "audit_signature": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "timestamp": "2026-07-24T18:35:00Z",
  "explanation": {
    "planning_process": "Plan 'plan-001': Target Horizon=LONG_TERM, Style=VALUE.",
    "task_graph_execution": "Task Graph 'graph-001': Total Tasks=5.",
    "final_confidence": 0.88
  }
}
```

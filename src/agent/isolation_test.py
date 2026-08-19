from src.agent.retention_agent import generate_retention_action
print(generate_retention_action({
    "customer_id": "12345", "recency_days": 95,
    "frequency": 8, "monetary": 620.50, "estimated_clv": 930.75
}))
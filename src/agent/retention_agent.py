import json
import requests
from src.config import Config
from src.agent.prompts import RETENTION_EMAIL_PROMPT
import re


def _call_ollama(prompt: str) -> str:
    resp = requests.post(
        f"{Config.OLLAMA_BASE_URL}/api/generate",
        json={"model": Config.OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def generate_retention_action(customer_row: dict, reasons: list = None) -> dict:
    risk_factors_text = "\n".join(
        f"- {r['label']} ({r['direction']})" for r in (reasons or [])
    ) or "No specific risk factors available."
    
    prompt = RETENTION_EMAIL_PROMPT.format( risk_factors=risk_factors_text,**customer_row) 

    if Config.LLM_PROVIDER == "ollama":
        raw = _call_ollama(prompt)

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Genuine fallback — only reached if no valid JSON could be extracted at all
    return {
        "subject": "We miss you!",
        "body": raw.strip(),
        "offer": "10% off your next order",
    }
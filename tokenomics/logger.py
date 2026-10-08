import json
from datetime import datetime

COST_PER_1K_INPUT = 0.0015    # Gemini 3.5 Flash-Lite pricing
COST_PER_1K_OUTPUT = 0.009

LOG_PATH = "tokenomics_log.jsonl"


def _cost(input_tokens: int, output_tokens: int) -> float:
    input_cost = (input_tokens / 1000) * COST_PER_1K_INPUT
    output_cost = (output_tokens / 1000) * COST_PER_1K_OUTPUT
    return input_cost + output_cost


def log(query: str, agent: str, input_tokens: int, output_tokens: int,
        echo: bool = True) -> dict:
    """Log token usage for a single agent/model call."""
    total_cost = _cost(input_tokens, output_tokens)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "agent": agent,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(total_cost, 6),
        "cost_per_1000_queries": round(total_cost * 1000, 2),
    }

    if echo:
        print(
            f"\n[TOKENOMICS] Agent: {agent} | Input: {input_tokens} | "
            f"Output: {output_tokens} | Cost: ${total_cost:.6f}"
        )

    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def log_total(query: str, calls: list[dict], echo: bool = True) -> dict:
    """Sum every agent call for one query into a single 'total' record.

    Each item in `calls` is a dict with input_tokens / output_tokens
    (and optionally 'agent' for the per-call breakdown)."""
    in_tok = sum(c.get("input_tokens", 0) for c in calls)
    out_tok = sum(c.get("output_tokens", 0) for c in calls)
    return log(query, agent="TOTAL", input_tokens=in_tok,
               output_tokens=out_tok, echo=echo)

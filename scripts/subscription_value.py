"""Subscription value analysis — value of paid coding-agent subscriptions over time.

Reads the cass canonical DB (conversations + agents) and computes, per month:
sessions, tokens, estimated market cost, tool calls, per-harness mix, top
models, subscription spend, and the value ratio (market value / sub cost).

Sessions are complete. Token/cost columns are partial (best Feb-Jun, missing
Jul-Aug in the cass ingest); coverage is reported per month so the reader can
see what is real vs missing. Muse sessions are NOT in cass — excluded until
the cass devs ship a muse connector.

Pure function; never raises on missing DB (returns empty + problem record).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

CASS_DB = Path.home() / ".local/share/coding-agent-search/agent_search.db"

# Monthly subscription costs. `since` = first month the plan is counted.
PLANS: dict[str, dict[str, Any]] = {
    "claude_code": {"cost": 20.0, "since": "2026-02", "label": "Claude Code $20"},
    "codex": {"cost": 20.0, "since": "2026-02", "label": "Codex $20"},
    "antigravity": {"cost": 20.0, "since": "2026-02", "label": "Antigravity $20"},
    "opencode_go": {"cost": 10.0, "since": "2026-07", "label": "OpenCode Go $10"},
}

# Harness -> subscription that pays for it (approximate attribution).
HARNESS_TO_PLAN: dict[str, str] = {
    "claude_code": "claude_code",
    "codex": "codex",
    "antigravity": "antigravity",
    "gemini": "antigravity",       # preview tier attributed to antigravity sub [approx]
    "opencode": "opencode_go",
    "pi_agent": "opencode_go",
    "hermes": "opencode_go",
    "qwen": "opencode_go",
}

# Fallback market rates ($ per 1M in/out) for cost estimation when cass's
# estimated_cost_usd is absent but tokens are present. Post-July-30 2026 prices.
MODEL_RATES: dict[str, tuple[float, float]] = {
    "deepseek-v4-flash": (0.14, 0.28),
    "deepseek/deepseek-v4-flash:free": (0.0, 0.0),
    "glm-5.2": (0.07, 0.22),
    "gpt-5.6-luna": (0.20, 1.20),
    "gpt-5.6-sol": (5.0, 30.0),
    "gpt-5.6-terra": (1.0, 6.0),
    "kimi-k3": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-opus-4-5": (15.0, 75.0),
    "claude-opus-4-6": (15.0, 75.0),
    "claude-opus-5": (5.0, 25.0),
    "gemini-3-flash": (0.10, 0.40),
    "gemini-3-flash-preview": (0.10, 0.40),
}
DEFAULT_RATE = (0.05, 0.15)  # conservative floor for unmapped models


def _month_of(ms: int) -> str:
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m")
    except Exception:
        return "?"


def _est_market_value(model: str | None, in_tok: int | None, out_tok: int | None) -> float | None:
    """Estimate market cost from tokens x rate when cass's own estimate is absent."""
    if in_tok is None and out_tok is None:
        return None
    pin, pout = MODEL_RATES.get((model or "").strip(), DEFAULT_RATE)
    tin = (in_tok or 0) / 1e6 * pin
    tout = (out_tok or 0) / 1e6 * pout
    return round(tin + tout, 4)


def build_subscription_value(problems: list[dict] | None = None) -> dict[str, Any]:
    if problems is None:
        problems = []
    if not CASS_DB.exists():
        problems.append({"path": str(CASS_DB), "reason": "cass DB not found; no subscription value data"})
        return {"source": "cass", "months": [], "plans": PLANS, "notes": ["cass DB missing"]}

    con = None
    try:
        con = sqlite3.connect(f"file:{CASS_DB}?mode=ro", uri=True)
        cur = con.cursor()
        cur.execute("SELECT id, slug FROM agents")
        agent_map = {aid: slug for aid, slug in cur.fetchall()}
        cur.execute(
            """SELECT started_at, agent_id, grand_total_tokens, estimated_cost_usd,
                      tool_call_count, primary_model, total_input_tokens, total_output_tokens
               FROM conversations WHERE started_at IS NOT NULL"""
        )
        rows = cur.fetchall()
    except Exception as e:
        if con:
            con.close()
        problems.append({"path": str(CASS_DB), "reason": f"DB query failed: {e}"})
        return {"source": "cass", "months": [], "plans": PLANS, "notes": ["cass query failed"]}
    finally:
        if con:
            con.close()

    months: dict[str, dict[str, Any]] = {}
    for started_at, agent_id, gt, est_cost, tool_calls, model, tin, tout in rows:
        m = _month_of(started_at)
        if m == "?":
            continue
        slot = months.setdefault(m, {
            "month": m, "sessions": 0, "with_tokens": 0, "with_cost": 0,
            "tokens_M": 0.0, "est_cost": 0.0, "market_value": 0.0, "tool_calls": 0,
            "harness": {}, "models": {}, "harness_value": {},
        })
        slot["sessions"] += 1
        mv = None
        if gt is not None:
            slot["with_tokens"] += 1
            slot["tokens_M"] += gt / 1e6
        if est_cost is not None:
            slot["with_cost"] += 1
            slot["est_cost"] += est_cost
            mv = est_cost
        else:
            mv = _est_market_value(model, tin, tout)
        if mv is not None and (tin or tout):
            slot["market_value"] += mv
        slot["tool_calls"] += tool_calls or 0
        slug = agent_map.get(agent_id, "unknown")
        slot["harness"][slug] = slot["harness"].get(slug, 0) + 1
        hv = slot["harness_value"].setdefault(slug, {"sessions": 0, "tokens_M": 0.0, "market_value": 0.0})
        hv["sessions"] += 1
        if gt is not None:
            hv["tokens_M"] += gt / 1e6
        if mv is not None and (tin or tout):
            hv["market_value"] += mv
        key = (model or "").strip() or "unknown"
        slot["models"][key] = slot["models"].get(key, 0) + 1

    out = []
    for m in sorted(months):
        slot = months[m]
        n = slot["sessions"]
        coverage = round(slot["with_tokens"] / n, 3) if n else 0.0
        sub_cost = sum(p["cost"] for p in PLANS.values() if m >= p["since"])
        market = round(slot["market_value"], 2)
        # plan attribution: harness -> plan -> sessions/tokens/value
        plans = {}
        for plan_id, plan in PLANS.items():
            if m < plan["since"]:
                continue
            ps, pt, pv = 0, 0.0, 0.0
            for slug, hv in slot["harness_value"].items():
                if HARNESS_TO_PLAN.get(slug) == plan_id:
                    ps += hv["sessions"]; pt += hv["tokens_M"]; pv += hv["market_value"]
            plans[plan_id] = {"sessions": ps, "tokens_M": round(pt, 1), "market_value": round(pv, 2)}
        out.append({
            "month": m,
            "sessions": n,
            "coverage_tokens": coverage,
            "tokens_M": round(slot["tokens_M"], 1),
            "est_cost": round(slot["est_cost"], 2),
            "market_value": market,
            "tool_calls": slot["tool_calls"],
            "sub_cost": sub_cost,
            "value_ratio": round(market / sub_cost, 2) if sub_cost and market else None,
            "cost_per_session": round(market / n, 3) if market and n else None,
            "tokens_per_dollar": round(slot["tokens_M"] * 1e6 / sub_cost) if sub_cost else None,
            "harness": slot["harness"],
            "plans": plans,
            "top_models": sorted(slot["models"].items(), key=lambda kv: -kv[1])[:6],
        })

    totals = {
        "sessions": sum(x["sessions"] for x in out),
        "tokens_M": round(sum(x["tokens_M"] for x in out), 1),
        "market_value": round(sum(x["market_value"] for x in out), 2),
        "sub_cost": sum(x["sub_cost"] for x in out),
        "months": len(out),
    }
    notes = [
        "Sessions are complete (cass canonical DB).",
        "Token/cost columns are partial: Jul-Aug 2026 absent at ingest (cass gap); coverage per month shown.",
        "Market value = cass estimated_cost_usd where present, else tokens x model rate (ARDF post-7/30 prices).",
        "Muse sessions are NOT in cass — excluded until a muse connector ships.",
        "Plan attribution approximate: opencode/pi/hermes/qwen -> OpenCode Go; gemini -> Antigravity [approx].",
        "OpenCode Go $10 counted from 2026-07; other plans from 2026-02.",
    ]
    return {"source": "cass conversations",
            "plans": {k: {"cost": v["cost"], "label": v["label"]} for k, v in PLANS.items()},
            "months": out, "totals": totals, "notes": notes}


if __name__ == "__main__":
    import json
    print(json.dumps(build_subscription_value(), indent=1, default=str))

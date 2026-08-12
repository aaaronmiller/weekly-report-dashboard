"""Claude Code section — local usage stats from ~/.claude/stats-cache.json.

Claude Code maintains a local usage cache with per-day activity (messages,
sessions, tool calls), per-day token usage by model, and per-model usage
totals (input/output/cache). This is harness-native data cass does not carry.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATS_CACHE = Path.home() / ".claude" / "stats-cache.json"


def build_claude_stats(problems: list[dict] | None = None) -> dict[str, Any]:
    if problems is None:
        problems = []
    if not STATS_CACHE.exists():
        problems.append({"path": str(STATS_CACHE), "reason": "claude stats-cache.json not found"})
        return {"days": [], "model_usage": [], "notes": ["stats-cache missing"]}
    try:
        d = json.loads(STATS_CACHE.read_text(encoding="utf-8"))
    except Exception as e:
        problems.append({"path": str(STATS_CACHE), "reason": f"parse failed: {e}"})
        return {"days": [], "model_usage": [], "notes": [f"parse failed: {e}"]}

    days = []
    daily = {x.get("date"): x for x in d.get("dailyActivity", [])}
    tokens = {x.get("date"): x for x in d.get("dailyModelTokens", [])}
    for date in sorted(set(list(daily.keys()) + list(tokens.keys()))):
        a = daily.get(date, {})
        t = tokens.get(date, {})
        by_model = t.get("tokensByModel", {})
        days.append({
            "date": date,
            "messages": a.get("messageCount", 0),
            "sessions": a.get("sessionCount", 0),
            "tool_calls": a.get("toolCallCount", 0),
            "tokens_total": sum(by_model.values()),
            "tokens_by_model": [{"model": k, "tokens": v} for k, v in
                                sorted(by_model.items(), key=lambda kv: -kv[1])],
        })

    mu = d.get("modelUsage", {})
    model_usage = [{
        "model": k,
        "input_tokens": v.get("inputTokens", 0),
        "output_tokens": v.get("outputTokens", 0),
        "cache_read": v.get("cacheReadInputTokens", 0),
        "cache_creation": v.get("cacheCreationInputTokens", 0),
        "cost_usd": v.get("costUSD", 0),
    } for k, v in sorted(mu.items(), key=lambda kv: -(kv[1].get("inputTokens", 0) + kv[1].get("outputTokens", 0)))]

    return {
        "source": "~/.claude/stats-cache.json (claude code local usage cache)",
        "last_computed": d.get("lastComputedDate"),
        "total_sessions": d.get("totalSessions"),
        "total_messages": d.get("totalMessages"),
        "days": days,
        "model_usage": model_usage,
        "notes": ["Harness-native cache; may lag until claude recomputes it (lastComputedDate shown).",
                  "costUSD is 0 under a subscription plan."],
    }


if __name__ == "__main__":
    print(json.dumps(build_claude_stats(), indent=1, default=str))

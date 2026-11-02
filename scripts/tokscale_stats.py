"""Tokscale cost/token statistics — real spend and usage from the tokscale CLI.

Runs `tokscale --offline --json --light` (no network; reads local session
files only) and reshapes the client/model entries into the dashboard's
canonical per-client spend table. This is the ONLY collector with verified
per-token cost attribution — cass/subscription_value estimates are marked
as such wherever both appear.

Pure function; never raises on missing binary or empty data (returns empty
+ problem record). Results are a current snapshot (no per-week history —
trayscale aggregates all local history), so freshness = build time.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

TOKSCALE_BIN = shutil.which("tokscale")


def _run_offline() -> dict[str, Any] | None:
    if not TOKSCALE_BIN:
        return None
    try:
        proc = subprocess.run(
            [TOKSCALE_BIN, "--no-spinner", "--offline", "--json", "--light"],
            capture_output=True, text=True, timeout=300,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except Exception:
        return None


def build_tokscale_stats(problems: list[dict] | None = None) -> dict[str, Any]:
    if problems is None:
        problems = []
    raw = _run_offline()
    if not raw:
        problems.append({
            "path": "tokscale",
            "reason": "tokscale binary missing or offline report failed",
        })
        return {}

    entries = raw.get("entries", []) if isinstance(raw, dict) else []
    clients: dict[str, dict[str, Any]] = {}
    for e in entries:
        c = e.get("client") or "unknown"
        d = clients.setdefault(c, {
            "client": c, "cost": 0.0, "messages": 0,
            "input": 0, "output": 0, "cache_read": 0, "cache_write": 0,
            "reasoning": 0, "models": [],
        })
        d["cost"] += e.get("cost") or 0.0
        d["messages"] += e.get("messageCount") or 0
        d["input"] += e.get("input") or 0
        d["output"] += e.get("output") or 0
        d["cache_read"] += e.get("cacheRead") or 0
        d["cache_write"] += e.get("cacheWrite") or 0
        d["reasoning"] += e.get("reasoning") or 0
        d["models"].append({
            "model": e.get("model"), "provider": e.get("provider"),
            "cost": round(e.get("cost") or 0.0, 2),
            "messages": e.get("messageCount") or 0,
            "input": e.get("input") or 0, "output": e.get("output") or 0,
            "cache_read": e.get("cacheRead") or 0,
            "cache_write": e.get("cacheWrite") or 0,
        })
    for d in clients.values():
        d["cost"] = round(d["cost"], 2)
        # deterministic: cost desc, then model/provider asc (zero-cost ties flipped otherwise)
        d["models"].sort(key=lambda m: (-m["cost"], m["model"] or "", m["provider"] or ""))

    by_client = sorted(clients.values(), key=lambda d: -d["cost"])
    total_cost = round(raw.get("totalCost") or sum(d["cost"] for d in by_client), 2)
    # No generated_at here: build time is stamped once by the pipeline
    # (payload.generated_at). A wall-clock field would break byte-identical
    # rebuilds (Gate 2 / SC-005). Freshness badge falls back to build time.
    return {
        "source": "tokscale --offline (local session files; verified per-token cost)",
        "total_cost": total_cost,
        "total_messages": raw.get("totalMessages", 0),
        "total_input": raw.get("totalInput", 0),
        "total_output": raw.get("totalOutput", 0),
        "total_cache_read": raw.get("totalCacheRead", 0),
        "total_cache_write": raw.get("totalCacheWrite", 0),
        "by_client": by_client,
    }


if __name__ == "__main__":
    print(json.dumps(build_tokscale_stats(), indent=1, default=str))

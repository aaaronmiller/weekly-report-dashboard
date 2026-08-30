"""Telemetry audit (M1) — consolidate provider x model x week from cass agent_search.db.

Answers: which model/provider combination does the work, at what cost, how fast,
and how often does it fail? Reads the canonical conversations table (already
aggregated per session by cass) — never parses raw session files at build time.

Constitution:
- stdlib only; read-only DB (mode=ro); corpus never written.
- Missing is not zero: weeks/models with no data are absent, not zero-filled.
- Isolate per-item failure: one unreadable row is skipped and counted, not fatal.
- Idempotent: output depends only on DB content.

Failure definition (observable, not inferred):
- primary_model = '<synthetic>'              -> cass recorded an API-error
  fallback conversation ("API Error: Unable to connect...").
- api_call_count = 0 AND tool_call_count = 0 -> degenerate session: nothing
  happened. (api_call_count alone is NOT a failure: some harnesses, e.g. qwen,
  do not report API counts but do run thousands of tool calls.)
Tool-call errors are NOT inferable from this corpus (1 marked error in 61k
tool messages) and are reported as absent, not zero.
"""
from __future__ import annotations

import json
import sqlite3
import statistics
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path("/home/cheta/.local/share/coding-agent-search/agent_search.db")
OUT_PATH = Path(__file__).parent.parent / "telemetry.json"

# The dashboard's week convention: weeks end Friday, covering Sat..Fri.
WEEK_END_WEEKDAY = 4  # Friday

# Operator's cost model (2026-08). Subscriptions are SUNK cost: list-price
# token cost on a subscribed harness is VALUE EXTRACTED, not money spent.
# Unused subscription quota is the waste to surface (Model Scan REQ-12.2).
SUBSCRIPTIONS = {
    "claude_code": {"provider": "anthropic", "quota_usd": 20.0},
    "codex":       {"provider": "openai",    "quota_usd": 20.0},
    "antigravity": {"provider": "google",    "quota_usd": 20.0},
    "opencode":    {"provider": "opencode-go", "quota_usd": 10.0},
}
# Everything else is free-tier or metered (openrouter free, opencode-zen free,
# muse at $0.10/$0.20 per Mtok — muse metered cost already lands in
# estimated_cost_usd via cass, so no special-casing needed here).
def cost_class(harness: str) -> str:
    return "subscription" if harness in SUBSCRIPTIONS else "free_or_metered"


def week_ending_for(ts_ms: int) -> str:
    """Map a millisecond timestamp to its week-ending Friday (YYYY-MM-DD)."""
    d = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).date()
    offset = (WEEK_END_WEEKDAY - d.weekday()) % 7
    return (d + timedelta(days=offset)).isoformat()


def build_telemetry(db_path: Path = DB_PATH, problems: list | None = None) -> dict:
    if problems is None:
        problems = []
    if not db_path.exists():
        problems.append({"path": str(db_path), "reason": "agent_search.db not found; no telemetry"})
        return {}

    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        rows = con.execute(
            """
            SELECT a.name            AS harness,
                   c.primary_model   AS model,
                   c.started_at      AS started_ms,
                   c.ended_at        AS ended_ms,
                   c.api_call_count,
                   c.tool_call_count,
                   c.total_input_tokens,
                   c.total_output_tokens,
                   c.total_cache_read_tokens,
                   c.estimated_cost_usd,
                   w.path            AS workspace_path
            FROM conversations c
            JOIN agents a ON a.id = c.agent_id
            LEFT JOIN workspaces w ON w.id = c.workspace_id
            WHERE c.started_at IS NOT NULL
            """
        ).fetchall()
    except Exception as e:
        problems.append({"path": str(db_path), "reason": f"query failed: {e}"})
        return {}
    finally:
        con.close()

    # week -> (harness, model) -> aggregate; plus month (quota) and project (value*) rolls
    weeks: dict[str, dict[tuple[str, str], dict]] = {}
    months: dict[str, dict[str, dict]] = {}     # month -> harness -> agg
    projects: dict[str, dict] = {}              # project -> agg
    skipped = 0
    for (harness, model, started_ms, ended_ms, api, tool, tin, tout, cache, cost, ws_path) in rows:
        try:
            started_dt = datetime.fromtimestamp(int(started_ms) / 1000, tz=timezone.utc)
            wk = week_ending_for(int(started_ms))
            h = harness or "unknown"
            key = (h, model or "unknown")
            agg = weeks.setdefault(wk, {}).setdefault(key, {
                "conversations": 0, "api_calls": 0, "tool_calls": 0,
                "tokens_in": 0, "tokens_out": 0, "cache_read": 0,
                "est_cost_usd": 0.0, "durations": [], "failed": 0,
            })
            month = started_dt.strftime("%Y-%m")
            m_agg = months.setdefault(month, {}).setdefault(h, {
                "conversations": 0, "tool_calls": 0, "est_cost_usd": 0.0,
                "failed": 0, "cost_observed": 0,
            })
            proj = Path(ws_path).name if ws_path else "unpathed"
            p_agg = projects.setdefault(proj, {
                "conversations": 0, "tool_calls": 0, "est_cost_usd": 0.0,
                "cost_observed": 0,
            })
            cval = float(cost) if cost is not None else None  # NULL stays missing (P-II)
            for target in (agg, m_agg, p_agg):
                target["conversations"] = target.get("conversations", 0) + 1
                target["tool_calls"] = target.get("tool_calls", 0) + int(tool or 0)
                if cval is not None:
                    target["est_cost_usd"] = target.get("est_cost_usd", 0.0) + cval
                    target["cost_observed"] = target.get("cost_observed", 0) + 1
            agg["api_calls"] += int(api or 0)
            agg["tokens_in"] += int(tin or 0)
            agg["tokens_out"] += int(tout or 0)
            agg["cache_read"] += int(cache or 0)
            if ended_ms and started_ms and ended_ms > started_ms:
                agg["durations"].append((int(ended_ms) - int(started_ms)) / 1000.0)
            m = model or ""
            if m == "<synthetic>" or (int(api or 0) == 0 and int(tool or 0) == 0):
                agg["failed"] += 1
                m_agg["failed"] += 1
        except Exception:
            skipped += 1
    if skipped:
        problems.append({"path": "conversations", "reason": f"{skipped} rows skipped (malformed)"})

    def finalize(agg: dict) -> dict:
        out = {k: v for k, v in agg.items() if k != "durations"}
        out["median_duration_s"] = round(statistics.median(agg["durations"]), 1) if agg["durations"] else None
        out["est_cost_usd"] = round(out["est_cost_usd"], 4)
        return out

    weeks_out = {
        wk: {
            "by_provider_model": [
                {"harness": h, "model": m, **finalize(agg)}
                for (h, m), agg in sorted(pm.items(), key=lambda kv: -kv[1]["tool_calls"])
            ]
        }
        for wk, pm in sorted(weeks.items())
    }

    # Overall top models across all weeks (the "which combination is best" answer)
    overall: dict[tuple[str, str], dict] = {}
    for pm in weeks.values():
        for (h, m), agg in pm.items():
            o = overall.setdefault((h, m), {
                "harness": h, "model": m, "conversations": 0, "api_calls": 0,
                "tool_calls": 0, "tokens_in": 0, "tokens_out": 0,
                "cache_read": 0, "est_cost_usd": 0.0, "durations": [], "failed": 0,
            })
            for k in ("conversations", "api_calls", "tool_calls", "tokens_in", "tokens_out", "cache_read", "est_cost_usd", "failed"):
                o[k] += agg[k]
            o["durations"].extend(agg.get("durations", []))
    top = sorted(overall.values(), key=lambda o: -o["tool_calls"])[:20]
    top_out = []
    for o in top:
        d = {k: v for k, v in o.items() if k != "durations"}
        d["median_duration_s"] = round(statistics.median(o["durations"]), 1) if o["durations"] else None
        d["est_cost_usd"] = round(d["est_cost_usd"], 4)
        d["failure_rate"] = round(d["failed"] / d["conversations"], 3) if d["conversations"] else None
        top_out.append(d)

    # --- Value* (subscription-first cost model) ---
    # Subscriptions are sunk; extracted list-price value vs quota = utilization.
    # cass stopped pricing subscription harnesses after 2026-06 (est cost NULL).
    # Per Principle II, utilization is null when cost is unobserved — never 0%.
    current_month = max(months.keys()) if months else None
    subs_out = []
    for harness, cfg in SUBSCRIPTIONS.items():
        cur = months.get(current_month, {}).get(harness, {})
        observed = cur.get("cost_observed", 0)
        extracted_cur = round(cur.get("est_cost_usd", 0.0), 2) if observed else None
        quota = cfg["quota_usd"]
        # Best observed month = the value* headline (what the sub delivered when priced)
        best = {"extracted": 0.0, "month": None}
        for mn, mm in months.items():
            a = mm.get(harness, {})
            if a.get("cost_observed", 0) and a.get("est_cost_usd", 0.0) > best["extracted"]:
                best = {"extracted": a["est_cost_usd"], "month": mn}
        subs_out.append({
            "harness": harness,
            "provider": cfg["provider"],
            "month": current_month,
            "quota_usd": quota,
            "extracted_usd": extracted_cur,
            "utilization": round(extracted_cur / quota, 3) if (quota and extracted_cur is not None) else None,
            "cost_observed": observed,
            "best_month": best["month"],
            "best_month_extracted_usd": round(best["extracted"], 2),
            "best_month_roi": round(best["extracted"] / quota, 1) if quota else None,
            "tool_calls": cur.get("tool_calls", 0),
            "conversations": cur.get("conversations", 0),
            "failed": cur.get("failed", 0),
        })

    # Work volume by cost class (all months): subscription vs free/metered
    class_totals = {"subscription": {"tool_calls": 0, "conversations": 0, "est_cost_usd": 0.0},
                    "free_or_metered": {"tool_calls": 0, "conversations": 0, "est_cost_usd": 0.0}}
    for month_map in months.values():
        for h, a in month_map.items():
            c = class_totals[cost_class(h)]
            c["tool_calls"] += a["tool_calls"]
            c["conversations"] += a["conversations"]
            c["est_cost_usd"] += a["est_cost_usd"]
    for c in class_totals.values():
        c["est_cost_usd"] = round(c["est_cost_usd"], 2)

    # $/project (all months, top by extracted value)
    proj_out = sorted(
        ({"project": p, **{k: (round(v, 2) if k == "est_cost_usd" else v) for k, v in a.items()}} for p, a in projects.items()),
        key=lambda x: -x["est_cost_usd"],
    )[:15]

    hv: dict[str, dict] = {}
    for month_map in months.values():
        for h, a in month_map.items():
            o = hv.setdefault(h, {"harness": h, "cost_class": cost_class(h), "conversations": 0, "tool_calls": 0, "est_cost_usd": 0.0})
            o["conversations"] += a["conversations"]
            o["tool_calls"] += a["tool_calls"]
            o["est_cost_usd"] += a["est_cost_usd"]
    harness_value = sorted(hv.values(), key=lambda o: -o["tool_calls"])
    for o in harness_value:
        o["est_cost_usd"] = round(o["est_cost_usd"], 2)
        o["usd_per_1k_tool_calls"] = round(o["est_cost_usd"] * 1000 / o["tool_calls"], 3) if o["tool_calls"] else None

    # Idempotence: generated_at derives from the newest observed session end,
    # not the wall clock (constitution: retrieved_at = max started_at).
    max_end_ms = max((int(r[3]) for r in rows if r[3]), default=None)
    generated_at = (
        datetime.fromtimestamp(max_end_ms / 1000, tz=timezone.utc).isoformat()
        if max_end_ms else None
    )
    return {
        "source": "cass agent_search.db conversations (read-only)",
        "generated_at": generated_at,
        "failure_definition": "model='<synthetic>' (cass API-error fallback) or api_calls=0 AND tool_calls=0 (degenerate)",
        "tool_call_errors": "not observable in this corpus; reported as absent, not zero",
        "cost_model": "subscriptions sunk ($20 anthropic/openai/google, $10 opencode-go); list-price = value extracted; unused quota = waste",
        "subscriptions": subs_out,
        "class_totals": class_totals,
        "by_project": proj_out,
        "value_by_harness": harness_value,
        "weeks": weeks_out,
        "top_models": top_out,
    }


if __name__ == "__main__":
    probs: list = []
    data = build_telemetry(problems=probs)
    OUT_PATH.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")))
    n_weeks = len(data.get("weeks", {}))
    n_models = len(data.get("top_models", []))
    print(f"Wrote {OUT_PATH} ({n_weeks} weeks, top {n_models} models)")
    for p in probs:
        print(f"  problem: {p.get('path')}: {p.get('reason')}")

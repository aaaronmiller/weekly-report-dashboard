"""Harness-standardized session statistics — one shared schema per harness.

Reads the cass canonical DB (conversations) and produces, per harness (and per
harness × month), a standardized table: sessions, duration (min/avg/median),
tool calls per session, API calls per session, tokens per session, model mix,
workspace (project) mix. This is the reusable schema every harness section
uses; muse is appended from its own session logs when present.

Pure function; never raises on missing DB.
"""
from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from statistics import median
from typing import Any

CASS_DB = Path.home() / ".local/share/coding-agent-search/agent_search.db"
MUSE_ROOT = Path.home() / ".local/share/muse/sessions"


def _month_of(ms: int) -> str:
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m")
    except Exception:
        return "?"


def _dur_minutes(started_ms, ended_ms):
    if not started_ms or not ended_ms or ended_ms <= started_ms:
        return None
    return round((ended_ms - started_ms) / 60000, 1)


def _muse_stats() -> dict[str, Any]:
    """Count muse session.jsonl files per month + estimate duration from model_completed events.
    Muse is not in cass; read directly. Best-effort, bounded."""
    months: dict[str, dict[str, Any]] = {}
    for f in MUSE_ROOT.glob("2026/*/*/*/session.jsonl"):
        month = f"{f.parent.parent.parent.parent.name}-{f.parent.parent.parent.name}"
        slot = months.setdefault(month, {"sessions": 0, "durations_min": [], "tool_calls": 0, "models": {}})
        slot["sessions"] += 1
        try:
            with open(f, "r", errors="replace") as fh:
                for line in fh:
                    if '"model_completed"' in line and '"duration_ms"' in line:
                        try:
                            d = json.loads(line)
                            ev = d.get("payload", {}).get("event", {})
                            slot["durations_min"].append(ev.get("duration_ms", 0) / 60000)
                        except Exception:
                            pass
        except Exception:
            pass
    out = []
    for month in sorted(months):
        s = months[month]
        ds = [d for d in s["durations_min"] if d > 0]
        out.append({
            "harness": "muse", "month": month, "sessions": s["sessions"],
            "avg_min": round(sum(ds) / len(ds), 1) if ds else None,
            "median_min": round(median(ds), 1) if ds else None,
            "total_min": round(sum(ds), 1) if ds else None,
            "tool_calls": s["tool_calls"],
        })
    return {"harness": "muse", "months": out}


def build_harness_stats(problems: list[dict] | None = None) -> dict[str, Any]:
    if problems is None:
        problems = []
    if not CASS_DB.exists():
        problems.append({"path": str(CASS_DB), "reason": "cass DB not found; no harness stats"})
        return {"harness": [], "months": []}
    con = None
    try:
        con = sqlite3.connect(f"file:{CASS_DB}?mode=ro", uri=True)
        cur = con.cursor()
        cur.execute("SELECT id, slug FROM agents")
        agent_map = {aid: slug for aid, slug in cur.fetchall()}
        cur.execute("""SELECT started_at, ended_at, agent_id, tool_call_count, api_call_count,
                              grand_total_tokens, primary_model, workspace_id
                       FROM conversations WHERE started_at IS NOT NULL""")
        rows = cur.fetchall()
        cur.execute("SELECT id, path FROM workspaces")
        ws_map = {wid: (Path(p).name if p else "?") for wid, p in cur.fetchall()}
    except Exception as e:
        if con:
            con.close()
        problems.append({"path": str(CASS_DB), "reason": f"DB query failed: {e}"})
        return {"harness": [], "months": []}
    finally:
        if con:
            con.close()

    harnesses: dict[str, dict[str, Any]] = {}
    months: dict[str, dict[str, Any]] = {}
    for started_at, ended_at, agent_id, tc, ac, tokens, model, wid in rows:
        slug = agent_map.get(agent_id, "unknown")
        m = _month_of(started_at)
        h = harnesses.setdefault(slug, {"harness": slug, "sessions": 0, "durations_min": [], "tool_calls": 0, "api_calls": 0, "tokens_M": 0.0, "models": {}, "workspaces": {}})
        h["sessions"] += 1
        d = _dur_minutes(started_at, ended_at)
        if d is not None:
            h["durations_min"].append(d)
        h["tool_calls"] += tc or 0
        h["api_calls"] += ac or 0
        if tokens:
            h["tokens_M"] += tokens / 1e6
        mk = (model or "").strip() or "unknown"
        h["models"][mk] = h["models"].get(mk, 0) + 1
        wname = ws_map.get(wid, "?")
        h["workspaces"][wname] = h["workspaces"].get(wname, 0) + 1
        # per-month per-harness rollup
        key = (m, slug)
        mm = months.setdefault(key, {"month": m, "harness": slug, "sessions": 0, "tool_calls": 0, "api_calls": 0, "tokens_M": 0.0})
        mm["sessions"] += 1
        mm["tool_calls"] += tc or 0
        mm["api_calls"] += ac or 0
        if tokens:
            mm["tokens_M"] += tokens / 1e6

    harness_out = []
    for slug in sorted(harnesses):
        h = harnesses[slug]
        ds = h["durations_min"]
        harness_out.append({
            "harness": slug, "sessions": h["sessions"],
            "avg_dur_min": round(sum(ds) / len(ds), 1) if ds else None,
            "median_dur_min": round(median(ds), 1) if ds else None,
            "tool_calls": h["tool_calls"],
            "tools_per_session": round(h["tool_calls"] / h["sessions"], 1) if h["sessions"] else None,
            "api_calls": h["api_calls"],
            "tokens_M": round(h["tokens_M"], 1),
            "top_models": sorted(h["models"].items(), key=lambda kv: -kv[1])[:5],
            "top_workspaces": sorted(h["workspaces"].items(), key=lambda kv: -kv[1])[:6],
        })
    month_out = sorted(({"month": k[0], "harness": k[1], **v} for k, v in months.items()),
                       key=lambda x: (x["month"], x["harness"]))

    muse = _muse_stats()
    return {"harness": harness_out, "months": month_out, "muse": muse,
            "source": "cass conversations + muse session dirs"}


if __name__ == "__main__":
    print(json.dumps(build_harness_stats(), indent=1, default=str))

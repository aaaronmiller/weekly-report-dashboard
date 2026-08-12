"""Projects section — what each project did: sessions, git commits, files,
tokens, models, tool calls, per month.

Sources: cass conversations (workspace -> sessions/tokens/tools/models/duration)
+ git log per repo under /home/cheta/code (commits + files changed per month).

Pure function; never raises; git scan is time-bounded and failure-isolated.
"""
from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path
from typing import Any
from statistics import median

CASS_DB = Path.home() / ".local/share/coding-agent-search/agent_search.db"
CODE_ROOT = Path.home() / "code"
GIT_BOUND = 60  # seconds cap for the whole git scan


def _month_of(ms: int) -> str:
    try:
        from datetime import datetime, timezone
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m")
    except Exception:
        return "?"


def _git_repos() -> list[Path]:
    repos = []
    for d in CODE_ROOT.iterdir():
        if (d / ".git").exists():
            repos.append(d)
    return sorted(repos)


def _git_stats(repo: Path, since: str = "2026-02-01") -> dict[str, Any]:
    """Commits + files changed per month for one repo. Never raises."""
    out = {"commits_by_month": {}, "files_by_month": {}, "total_commits": 0}
    try:
        r = subprocess.run(
            ["git", "log", f"--since={since}", "--date=short", "--format=%ad"],
            cwd=repo, capture_output=True, text=True, timeout=8)
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                m = line[:7]
                if len(m) == 7:
                    out["commits_by_month"][m] = out["commits_by_month"].get(m, 0) + 1
                    out["total_commits"] += 1
        r2 = subprocess.run(
            ["git", "log", f"--since={since}", "--date=short", "--format=%ad", "--shortstat"],
            cwd=repo, capture_output=True, text=True, timeout=8)
        if r2.returncode == 0:
            cur = None
            for line in r2.stdout.splitlines():
                if line.startswith("2") and len(line) >= 10 and line[4] == "-":
                    cur = line[:7]
                elif "files changed" in line:
                    try:
                        n = int(line.split(",")[0].split()[0])
                        if cur:
                            out["files_by_month"][cur] = out["files_by_month"].get(cur, 0) + n
                    except Exception:
                        pass
    except Exception:
        pass
    return out


def build_projects_stats(problems: list[dict] | None = None) -> dict[str, Any]:
    if problems is None:
        problems = []
    # --- cass side: per-workspace session rollup ---
    ws: dict[str, dict[str, Any]] = {}
    if CASS_DB.exists():
        try:
            con = sqlite3.connect(f"file:{CASS_DB}?mode=ro", uri=True)
            cur = con.cursor()
            cur.execute("SELECT id, path FROM workspaces")
            ws_map = {wid: (Path(p).name if p else "?") for wid, p in cur.fetchall()}
            cur.execute("""SELECT workspace_id, started_at, ended_at, tool_call_count,
                                  api_call_count, grand_total_tokens, primary_model
                           FROM conversations WHERE started_at IS NOT NULL""")
            for wid, started, ended, tc, ac, tokens, model in cur.fetchall():
                name = ws_map.get(wid, "?") or "?"
                slot = ws.setdefault(name, {"project": name, "sessions": 0, "tool_calls": 0,
                                            "api_calls": 0, "tokens_M": 0.0, "models": {},
                                            "durations_min": [], "by_month": {}})
                slot["sessions"] += 1
                slot["tool_calls"] += tc or 0
                slot["api_calls"] += ac or 0
                if tokens:
                    slot["tokens_M"] += tokens / 1e6
                mk = (model or "").strip() or "unknown"
                slot["models"][mk] = slot["models"].get(mk, 0) + 1
                if started and ended and ended > started:
                    slot["durations_min"].append((ended - started) / 60000)
                m = _month_of(started)
                slot["by_month"][m] = slot["by_month"].get(m, 0) + 1
            con.close()
        except Exception as e:
            problems.append({"path": str(CASS_DB), "reason": f"workspace query failed: {e}"})
    else:
        problems.append({"path": str(CASS_DB), "reason": "cass DB not found; no project sessions"})

    # --- git side: commits + files per repo ---
    git_rows: dict[str, dict[str, Any]] = {}
    import time
    deadline = time.time() + GIT_BOUND
    for repo in _git_repos():
        if time.time() > deadline:
            problems.append({"path": "git scan", "reason": "git scan hit time bound; some repos skipped"})
            break
        g = _git_stats(repo)
        if g["total_commits"]:
            git_rows[repo.name] = g

    # merge: project = workspace name or repo name
    project_names = sorted(set(list(ws.keys()) + list(git_rows.keys())))
    projects = []
    for name in project_names:
        w = ws.get(name, {})
        g = git_rows.get(name, {})
        ds = w.get("durations_min", [])
        projects.append({
            "project": name,
            "sessions": w.get("sessions", 0),
            "avg_dur_min": round(sum(ds) / len(ds), 1) if ds else None,
            "tool_calls": w.get("tool_calls", 0),
            "tools_per_session": round(w["tool_calls"] / w["sessions"], 1) if w.get("sessions") else None,
            "api_calls": w.get("api_calls", 0),
            "tokens_M": round(w.get("tokens_M", 0.0), 1),
            "commits": g.get("total_commits", 0),
            "commits_by_month": g.get("commits_by_month", {}),
            "files_by_month": g.get("files_by_month", {}),
            "top_models": sorted(w.get("models", {}).items(), key=lambda kv: -kv[1])[:4],
            "sessions_by_month": w.get("by_month", {}),
        })
    projects.sort(key=lambda p: -(p["sessions"] + p["commits"]))

    # monthly aggregate for charts: merge git + sessions across projects
    months: dict[str, dict[str, Any]] = {}
    for p in projects:
        for m, c in p["commits_by_month"].items():
            months.setdefault(m, {"month": m, "commits": 0, "files": 0, "sessions": 0})["commits"] += c
        for m, c in p["files_by_month"].items():
            months.setdefault(m, {"month": m, "commits": 0, "files": 0, "sessions": 0})["files"] += c
        for m, c in p["sessions_by_month"].items():
            months.setdefault(m, {"month": m, "commits": 0, "files": 0, "sessions": 0})["sessions"] += c
    month_out = sorted(months.values(), key=lambda x: x["month"])

    # momentum: per-project delta between the two most recent active months
    from collections import defaultdict
    for p in projects:
        sm = p["sessions_by_month"]
        cm = p["commits_by_month"]
        active = sorted(set(list(sm.keys()) + list(cm.keys())))
        p["momentum"] = None
        if len(active) >= 2:
            last, prev = active[-1], active[-2]
            cur = sm.get(last, 0) + cm.get(last, 0)
            prior = sm.get(prev, 0) + cm.get(prev, 0)
            if prior > 0:
                p["momentum"] = round((cur - prior) / prior, 2)
    return {"projects": projects, "months": month_out,
            "source": "cass workspaces + git log (code/)",
            "notes": ["Git scan bounded at 60s; repos beyond the cap are skipped and noted.",
                      "Sessions per project come from cass workspace attribution."]}


if __name__ == "__main__":
    import json
    print(json.dumps(build_projects_stats(), indent=1, default=str))

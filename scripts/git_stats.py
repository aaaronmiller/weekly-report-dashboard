"""Git audit section — repo health from the nightly repo-sync report.

Primary source: ~/.local/state/cronjobs/repo-health.json (stable merged
report emitted by cronjobs repo-sync check). Fallback: newest
~/git-audit-logs/git-audit-*.json. This is the git-audit-sync data
surfaced as its own page — parallel to, not merged into, project stats.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path
from typing import Any

STABLE = Path.home() / ".local" / "state" / "cronjobs" / "repo-health.json"
AUDIT_GLOB = str(Path.home() / "git-audit-logs" / "git-audit-*.json")


def build_git_stats(problems: list[dict] | None = None) -> dict[str, Any]:
    if problems is None:
        problems = []

    data = None
    source = None
    if STABLE.exists():
        try:
            data = json.loads(STABLE.read_text(encoding="utf-8"))
            source = str(STABLE)
        except Exception as e:
            problems.append({"path": str(STABLE), "reason": f"parse failed: {e}"})

    if data is None:
        files = sorted(glob.glob(AUDIT_GLOB), reverse=True)
        for f in files:
            try:
                data = json.loads(Path(f).read_text(encoding="utf-8"))
                source = f
                break
            except Exception:
                continue
        if data is None:
            problems.append({"path": "git-audit-logs", "reason": "no repo-health.json or git-audit-*.json found"})
            return {"health_pct": None, "stats": {}, "repos": [], "source": None, "notes": ["no git audit data"]}

    repos = data.get("repos", []) or []
    stats = data.get("stats", {}) or {}

    # Normalize rows for the table.
    rows = []
    dirty_count = 0
    for r in repos:
        state = r.get("state") or "unknown"
        uncommitted = r.get("uncommitted") or 0
        ahead = r.get("ahead") or 0
        behind = r.get("behind") or 0
        if state in ("dirty", "conflicted", "dirty-even", "dirty-odd") or uncommitted or ahead or behind:
            dirty_count += 1
        rows.append({
            "name": r.get("name", "?"),
            "state": state,
            "branch": r.get("branch"),
            "uncommitted": uncommitted,
            "ahead": ahead,
            "behind": behind,
        })
    rows.sort(key=lambda r: (r["state"] != "clean", -(r["uncommitted"] + r["ahead"] + r["behind"])))

    return {
        "health_pct": data.get("health_pct"),
        "generated_at": data.get("generated_at") or data.get("timestamp"),
        "stats": stats,
        "roots": data.get("roots"),
        "excluded": data.get("excluded"),
        "repos": rows,
        "dirty_count": dirty_count,
        "total": len(rows),
        "source": source,
        "notes": [
            "Source: cronjobs repo-sync check (nightly 03:00), stable report repo-health.json.",
            "Dirty/conflicted/ahead/behind rows sort first; clean rows are the baseline.",
        ],
    }


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(build_git_stats(), indent=1, default=str))

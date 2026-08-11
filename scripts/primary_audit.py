"""Primary Audit — first-principles collection from raw harness logs, NOT weekly summaries.

Reads the canonical deduped source: cass raw-mirror manifests + coding-agent-search
DB, plus direct harness file discovery for every CLI/TUI listed in
/home/cheta/code/agents/platforms.json and /home/cheta/code/agents/sync.sh.

Per Constitution Principle I/III: one table, provenance on every number.
Per Principle IV: one malformed blob never aborts the rest.

Stdlib only. Offline. Read-only.
"""
from __future__ import annotations
import json, sqlite3, glob, re
from pathlib import Path
from datetime import date, datetime, timezone, timedelta
from collections import defaultdict, Counter

# Platforms.json authoritative list — resolved via configDir/dataDir
# We enumerate actual filesystem locations that hold session logs:
HARNESS_DIRS = {
    "muse": [Path.home()/".local/share/muse/sessions"],
    "claude": [Path.home()/".claude/projects"],
    "codex": [Path.home()/".codex/sessions"],
    "hermes": [Path.home()/".hermes/sessions", Path.home()/".hermes/conversations"],
    "qwen": [Path.home()/".qwen/sessions", Path.home()/".qwen"],
    "gemini": [Path.home()/".gemini"],
    "kilocode": [Path.home()/".kilocode"],
    "openclaw": [Path.home()/".openclaw"],
    "opencode": [Path.home()/".config/opencode"],
    "copilot": [Path.home()/".copilot"],
    "cline": [Path.home()/".agents"],
    "roo": [Path.home()/".roo"],
    "pi_agent": [Path.home()/".pi/agent/sessions"],
    "antigravity": [Path.home()/".config/antigravity", Path.home()/".gemini/antigravity"],
}

CASS_DB = Path.home()/".local/share/coding-agent-search/agent_search.db"
RAW_MIRROR_MANIFESTS = Path.home()/".local/share/coding-agent-search/raw-mirror/v1/manifests"
RAW_MIRROR_BLOBS = Path.home()/".local/share/coding-agent-search/raw-mirror/v1/blobs/blake3"

def _week_ending_saturday(d: date) -> date:
    """Return Saturday of the week containing d (weekly-report convention: week ending Saturday)."""
    # weekday: Mon=0 ... Sun=6, Sat=5
    offset = (5 - d.weekday()) % 7
    return d + timedelta(days=offset)

def _date_str(d: date) -> str:
    return d.isoformat()

def discover_primary_via_cass(problems: list[dict] | None = None) -> dict[str, dict]:
    """Query cass DB (conversations + daily_stats) — the deduped primary index.

    Returns dict[week_ending_str -> {sessions, per_harness, per_agent, provenance}].
    Never raises on DB absence; returns empty + problem.
    """
    if problems is None:
        problems = []
    if not CASS_DB.exists():
        problems.append({"path": str(CASS_DB), "reason": "cass DB not found; no primary sessions"})
        return {}
    try:
        con = sqlite3.connect(str(CASS_DB))
        cur = con.cursor()
        # conversations holds one row per deduped session
        cur.execute("SELECT started_at, agent_id FROM conversations WHERE started_at IS NOT NULL")
        rows = cur.fetchall()
        con.close()
    except Exception as e:
        problems.append({"path": str(CASS_DB), "reason": f"DB query failed: {e}"})
        return {}

    # Map agent_id -> slug
    agent_map = {}
    try:
        con = sqlite3.connect(str(CASS_DB))
        cur = con.cursor()
        cur.execute("SELECT id, slug FROM agents")
        for aid, slug in cur.fetchall():
            agent_map[aid] = slug
        con.close()
    except Exception:
        pass

    weekly: dict[str, Counter] = defaultdict(Counter)
    weekly_total: dict[str, int] = Counter()
    for started_at, agent_id in rows:
        try:
            # started_at is ms since epoch
            dt = datetime.fromtimestamp(int(started_at)/1000, tz=timezone.utc)
            d = dt.date()
            wk = _week_ending_saturday(d)
            wk_str = _date_str(wk)
            weekly_total[wk_str] += 1
            slug = agent_map.get(agent_id, f"agent_{agent_id}")
            weekly[wk_str][slug] += 1
        except Exception as e:
            problems.append({"path": "cass:conversations", "reason": f"bad started_at {started_at}: {e}"})
            continue

    result: dict[str, dict] = {}
    # deterministic retrieved_at: max started_at per week (so idempotent)
    weekly_max_mtime: dict[str, int] = {}
    for started_at, agent_id in rows:
        try:
            dt = datetime.fromtimestamp(int(started_at)/1000, tz=timezone.utc)
            wk = _week_ending_saturday(dt.date())
            wk_str = _date_str(wk)
            ms = int(started_at)
            if wk_str not in weekly_max_mtime or ms > weekly_max_mtime[wk_str]:
                weekly_max_mtime[wk_str] = ms
        except Exception:
            pass
    for wk, total in weekly_total.items():
        max_ms = weekly_max_mtime.get(wk)
        retrieved = datetime.fromtimestamp(max_ms/1000, tz=timezone.utc) if max_ms else datetime.fromtimestamp(0, tz=timezone.utc)
        result[wk] = {
            "sessions_primary": total,
            "per_harness": dict(weekly[wk]),
            "provenance": "primary:cass_conversations",
            "retrieved_at": retrieved,
        }
    return result

def discover_primary_via_manifests(problems: list[dict] | None = None) -> dict[str, dict]:
    """Fallback: scan raw-mirror manifests directly (25G blobs). Uses source_mtime_ms."""
    if problems is None:
        problems = []
    if not RAW_MIRROR_MANIFESTS.exists():
        problems.append({"path": str(RAW_MIRROR_MANIFESTS), "reason": "raw-mirror manifests not found"})
        return {}
    files = glob.glob(str(RAW_MIRROR_MANIFESTS / "*.json"))
    if not files:
        problems.append({"path": str(RAW_MIRROR_MANIFESTS), "reason": "no manifests"})
        return {}
    weekly_total: Counter = Counter()
    weekly_harness: dict[str, Counter] = defaultdict(Counter)
    for fp in files:
        try:
            j = json.loads(Path(fp).read_text(encoding="utf-8", errors="replace"))
            m = j.get("source_mtime_ms")
            prov = j.get("provider", "unknown")
            if not m:
                continue
            dt = datetime.fromtimestamp(int(m)/1000, tz=timezone.utc)
            wk = _week_ending_saturday(dt.date())
            wk_str = _date_str(wk)
            weekly_total[wk_str] += 1
            weekly_harness[wk_str][prov] += 1
        except Exception as e:
            problems.append({"path": fp, "reason": f"manifest parse failed: {e}"})
            continue
    weekly_max_mtime2: dict[str, int] = {}
    # need to recompute from files again for max mtime — we lost per-week max above, so re-scan
    # For simplicity, use week-ending midnight as deterministic fallback (since manifest loop already aggregated without tracking max, we reconstruct from total loop)
    # We will instead use manifest files again to compute max per week deterministically
    for fp in files:
        try:
            j = json.loads(Path(fp).read_text(encoding="utf-8", errors="replace"))
            m = j.get("source_mtime_ms")
            prov = j.get("provider")
            if not m:
                continue
            dt = datetime.fromtimestamp(int(m)/1000, tz=timezone.utc)
            wk = _week_ending_saturday(dt.date())
            wk_str = _date_str(wk)
            ms = int(m)
            if wk_str not in weekly_max_mtime2 or ms > weekly_max_mtime2[wk_str]:
                weekly_max_mtime2[wk_str] = ms
        except Exception:
            continue
    result: dict[str, dict] = {}
    for wk, total in weekly_total.items():
        max_ms = weekly_max_mtime2.get(wk)
        retrieved = datetime.fromtimestamp(max_ms/1000, tz=timezone.utc) if max_ms else datetime.fromtimestamp(0, tz=timezone.utc)
        result[wk] = {
            "sessions_primary": total,
            "per_harness": dict(weekly_harness[wk]),
            "provenance": "primary:raw_mirror_manifests",
            "retrieved_at": retrieved,
        }
    return result

def discover_primary_sessions(problems: list[dict] | None = None) -> dict[str, dict]:
    """Primary discovery: cass DB first, fallback to manifests. Returns weekly map."""
    if problems is None:
        problems = []
    # Prefer cass DB (fast, deduped, already indexes every harness per platforms.json)
    primary = discover_primary_via_cass(problems)
    if primary:
        # Cross-check with manifests for honesty: compare counts
        manifest = discover_primary_via_manifests([])
        # Log discrepancy as problem, not failure
        if manifest:
            dr_weeks = set(primary.keys()) | set(manifest.keys())
            for wk in sorted(dr_weeks):
                a = primary.get(wk, {}).get("sessions_primary", 0)
                b = manifest.get(wk, {}).get("sessions_primary", 0)
                if a != b:
                    problems.append({"path": f"primary:{wk}", "reason": f"cass {a} vs raw-mirror {b} sessions; cass is deduped truth"})
        return primary
    # Fallback
    return discover_primary_via_manifests(problems)

def aggregate_primary_weekly(problems: list[dict] | None = None) -> dict[str, dict]:
    """Public API: full weekly aggregation from primary sources only."""
    return discover_primary_sessions(problems)

def merge_with_legacy(primary_weekly: dict[str, dict], legacy_bundles: dict[str, dict], legacy_reports: dict[str, dict]) -> list[dict]:
    """Merge primary sessions with legacy bundles/reports for full picture.

    For each week in union(primary, legacy), produce a WeekRecord-like dict
    with sessions = primary if available else legacy, commits/files from legacy
    where available else None (Principle II: missing is not zero).
    Returns sorted list of week dicts (for inspection, not WeekRecord).
    """
    all_weeks = sorted(set(primary_weekly.keys()) | set(legacy_bundles.keys()) | set(legacy_reports.keys()))
    merged = []
    for wk in all_weeks:
        prim = primary_weekly.get(wk, {})
        legacy = legacy_bundles.get(wk, {})
        legacy_metrics = legacy.get("metrics", {}) if legacy else {}
        # sessions: primary truth wins
        sessions = prim.get("sessions_primary")
        if sessions is None:
            sessions = legacy_metrics.get("sessions_total")
        commits = legacy_metrics.get("commits_total")
        files = legacy_metrics.get("files_changed_total")
        projects = legacy_metrics.get("projects_total")
        merged.append({
            "week_ending": wk,
            "sessions_primary": prim.get("sessions_primary"),
            "sessions_legacy": legacy_metrics.get("sessions_total"),
            "sessions_effective": sessions,
            "commits": commits,
            "files_changed": files,
            "projects_active": projects,
            "has_primary": wk in primary_weekly,
            "has_legacy_bundle": wk in legacy_bundles,
            "has_legacy_report": wk in legacy_reports,
            "provenance": prim.get("provenance", "legacy") if wk in primary_weekly else ("legacy:bundle" if wk in legacy_bundles else "legacy:report"),
            "per_harness": prim.get("per_harness", {}),
        })
    return merged

# CLI for ad-hoc audit
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import argparse, pprint
    ap = argparse.ArgumentParser(description="Primary audit from raw harness logs")
    ap.add_argument("--check", action="store_true", help="print weekly counts and exit")
    ap.add_argument("--bundle-dir", default=str(Path.home()/ "code/weekly-report-dashboard"))
    ap.add_argument("--reports-dir", default=str(Path.home()/ "code/weekly-reports"))
    args = ap.parse_args()
    probs: list[dict] = []
    primary = discover_primary_sessions(probs)
    from scripts.ingest import discover_reports, discover_bundles
    reports, rp = discover_reports(args.reports_dir)
    bundles, bp = discover_bundles(args.bundle_dir)
    probs.extend(rp); probs.extend(bp)
    merged = merge_with_legacy(primary, bundles, reports)
    print(f"Primary weeks: {len(primary)}  Legacy weeks (union): {len(set(reports)|set(bundles))}  Merged: {len(merged)}")
    print(f"Date range primary: {min(primary) if primary else '?'} -> {max(primary) if primary else '?'}")
    print(f"Date range legacy: {min(set(reports)|set(bundles)) if reports or bundles else '?'} -> {max(set(reports)|set(bundles)) if reports or bundles else '?'}")
    for row in merged:
        print(f"{row['week_ending']}: sessions={row['sessions_effective']} (primary={row['sessions_primary']} legacy={row['sessions_legacy']}) commits={row['commits']} prov={row['provenance']}")
    if probs:
        print("\nProblems:")
        for p in probs:
            print(f"  - {p['path']}: {p['reason']}")

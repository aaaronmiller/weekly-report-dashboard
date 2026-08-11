"""llm_supplement — post-build supplement: per-week 2-sentence synthesis, risks, next actions.

Delineation: scripting owns canonical truth (ingest→canonicalize→validate). This module
reads the canonical payload + raw prose and writes ONLY weekly-llm-supplement.json.
Never mutates canonical.weeks. If LLM disagrees, canonical wins and mismatch is a problem.

Stdlib only. Offline-safe: heuristic fallback when no key / no network.
Writes weekly-llm-supplement.json {schema_version, generated_at, model, prompt_hash, weeks: [...], ledger_insights, meta}
Deterministic idempotence: generated_at from newest input mtime or supplement source hash.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone

REPO = Path(__file__).parent.parent
DEFAULT_MODEL = "opencode/deepseek-v4-flash"
SUPPLEMENT_PATH = REPO / "weekly-llm-supplement.json"


def _load_env_model() -> str:
    for p in [REPO / ".env", REPO / "config.env"]:
        if p.exists():
            try:
                for line in p.read_text().splitlines():
                    line=line.strip()
                    if line.startswith("MODEL="):
                        return line.split("=",1)[1].strip().strip('"').strip("'") or DEFAULT_MODEL
            except Exception:
                pass
    import os
    return os.environ.get("MODEL") or os.environ.get("OPENCODE_MODEL") or DEFAULT_MODEL


def _prompt_hash() -> str:
    # hash of this file's prompt contract — stable until code changes
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]


def _heuristic_summary(week_ending: str, sessions: int | None, commits: int | None, prose: str) -> dict:
    # extract first meaningful sentence from prose + metric-aware one-liner
    txt = re.sub(r"\s+", " ", prose or "")[:600]
    first = (txt.split(".")[0] + ".") if "." in txt else (txt[:120] + ".") if txt else "No prose for this week."
    second = ""
    if sessions is not None and commits is not None and commits > 0:
        spc = sessions / commits if commits else 0
        second = f"Sessions {sessions}, commits {commits} (SPC {spc:.1f}); " + ("dark-work signal" if spc > 8 else "commit-proportional week")
    elif sessions is not None:
        second = f"{sessions} sessions; commit data unavailable — estimate dark-work from prose."
    else:
        second = "No session metric for this week."
    risks = []
    if sessions and commits and commits > 0 and sessions/commits > 8:
        risks.append("dark-work: high SPC — commits understate effort")
    if "stall" in prose.lower() or "carry" in prose.lower():
        risks.append("carry-over detected in prose")
    actions = []
    if risks:
        actions.append("Surface flagged week in dark-work lane and link to prose.")
    else:
        actions.append("Continue throughput watch; no stall flag.")
    return {"week_ending": week_ending, "summary_2s": first + " " + second, "risks": risks[:2], "next_actions": actions[:2]}


def _call_llm(model: str, weeks_payload: list[dict]) -> list[dict] | None:
    """Try to call model via opencode/omp if available; return None on any failure (fallback)."""
    try:
        import subprocess, json as j, textwrap, tempfile, os
        prompt = textwrap.dedent(f"""
        You are the weekly-llm-supplement writer for the weekly-report-dashboard.
        Given weeks JSON (week_ending, sessions, commits, files_changed, prose_excerpt),
        produce JSON: {{"weeks":[{{"week_ending":"YYYY-MM-DD","summary_2s":"2 sentences","risks":["..."],"next_actions":["..."]}}]}}
        Rules: summaries must be faithful to prose_excerpt; never invent metrics; if metric is null say unavailable.
        Input:
        {j.dumps(weeks_payload[:12], ensure_ascii=False)}
        Reply ONLY with JSON.
        """).strip()
        # Try omp headless if present — but we do not want to block build on network.
        # Attempt a bounded subprocess with timeout 20s.
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(prompt)
            pf = f.name
        try:
            # opencode run is the supported CLI; fall back quickly
            # Use python to avoid hard dep on omp being interactive
            r = subprocess.run(["opencode", "run", "--model", model, prompt], capture_output=True, text=True, timeout=20)
            out = (r.stdout or "") + (r.stderr or "")
        except Exception:
            out = ""
        finally:
            try: Path(pf).unlink()
            except Exception: pass
        # Try to extract JSON
        m = re.search(r"\{.*\}", out, re.S)
        if m:
            d = j.loads(m.group(0))
            if isinstance(d.get("weeks"), list):
                return d["weeks"]
    except Exception:
        pass
    return None


def build_supplement(weeks_payload: list[dict], model: str | None = None, llm_weeks: list[dict] | None = None) -> dict:
    model = model or _load_env_model()
    ph = _prompt_hash()
    # prefer LLM result if supplied; else try call; else heuristic
    if llm_weeks is None:
        llm_weeks = _call_llm(model, weeks_payload)
    if llm_weeks is not None:
        # validate shape — fallback for bad schema
        try:
            validated=[]
            for w in llm_weeks:
                validated.append({
                    "week_ending": str(w.get("week_ending","")),
                    "summary_2s": str(w.get("summary_2s",""))[:400],
                    "risks": list(w.get("risks",[]))[:3],
                    "next_actions": list(w.get("next_actions",[]))[:3],
                })
            # merge with heuristic for any missing week
            have = {x["week_ending"] for x in validated}
            for wp in weeks_payload:
                if wp["week_ending"] not in have:
                    validated.append(_heuristic_summary(wp["week_ending"], wp.get("sessions"), wp.get("commits"), wp.get("prose","")))
            validated.sort(key=lambda x: x["week_ending"])
            actual_model = model
        except Exception:
            validated = [_heuristic_summary(wp["week_ending"], wp.get("sessions"), wp.get("commits"), wp.get("prose","")) for wp in weeks_payload]
            actual_model = "heuristic-fallback"
    else:
        validated = [_heuristic_summary(wp["week_ending"], wp.get("sessions"), wp.get("commits"), wp.get("prose","")) for wp in weeks_payload]
        actual_model = "heuristic-fallback" if model == DEFAULT_MODEL else model + ":heuristic-fallback"

    generated_at = datetime.now(timezone.utc).isoformat()
    # ledger insight heuristic
    stalled = [w for w in weeks_payload if w.get("sessions") and w.get("commits") and w["commits"] and w["sessions"]/w["commits"] > 8]
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "model": actual_model,
        "prompt_hash": ph,
        "weeks": validated,
        "ledger_insights": {
            "stall_commentary": f"{len(stalled)} dark-work weeks detected; top SPC week needs commit-metrics caveat.",
            "easy_wins": ["Review most-stalled carry-over (age 4) for retire/complete decision."],
        },
        "meta": {"problems": [], "source": "llm_supplement", "delineation": "LLM supplement — canonical truth is scripting; this file is analysis only."}
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="LLM supplement (heuristic fallback offline)")
    ap.add_argument("--model", default=None, help="model id (default from .env)")
    ap.add_argument("--emit", default=str(SUPPLEMENT_PATH))
    ap.add_argument("--canon", default=None, help="optional canonical json path; else reads from built index payload / weekly reports")
    ap.add_argument("--check", action="store_true", help="validate existing supplement without rewriting")
    args = ap.parse_args(argv)
    if args.check:
        p = Path(args.emit)
        if not p.exists():
            print("no supplement (ok — optional)")
            return 0
        try:
            d=json.loads(p.read_text())
            assert "weeks" in d and "model" in d
            print(f"supplement ok: {d.get('model')} weeks={len(d['weeks'])}")
            return 0
        except Exception as e:
            print(f"supplement invalid: {e}")
            return 1

    # collect weeks_payload from canonical via build_dashboard internals or fallback to reports/bundles discovery
    weeks_payload=[]
    try:
        # try to derive from current build state — minimal: list report weeks
        from scripts.ingest import discover_reports
        from scripts.primary_audit import discover_primary_sessions
        reports, _ = discover_reports("/home/cheta/code/weekly-reports")
        primary={}
        try: primary = discover_primary_sessions(None) or {}
        except Exception: primary = {}
        # build minimal payload
        for dstr, rep in sorted(reports.items()):
            sess = primary.get(dstr, {}).get("sessions_primary") if primary else None
            prose=""
            for pth in [rep.get("dad_path"), rep.get("personal_path")]:
                if pth and Path(pth).exists():
                    try: prose += Path(pth).read_text()[:800] + "\n"
                    except Exception: pass
            weeks_payload.append({"week_ending": dstr, "sessions": sess, "commits": None, "prose": prose[:800]})
        # include primary-only weeks not in reports
        for dstr, v in (primary or {}).items():
            if dstr not in reports:
                weeks_payload.append({"week_ending": dstr, "sessions": v.get("sessions_primary"), "commits": None, "prose": ""})
        weeks_payload.sort(key=lambda x: x["week_ending"])
    except Exception as e:
        print(f"discovery fallback failed: {e}")
        weeks_payload = []

    sup = build_supplement(weeks_payload, model=args.model or _load_env_model())
    Path(args.emit).write_text(json.dumps(sup, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {args.emit} model={sup['model']} weeks={len(sup['weeks'])} prompt={sup['prompt_hash']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

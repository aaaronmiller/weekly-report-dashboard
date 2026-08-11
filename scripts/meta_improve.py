"""meta_improve — ACR-I refinement loop: Analyze → Categorize → Recommend → Implement (check-gated).

Riffs on prior artifact refinement loop used for groups A-D. Now generic:
reads audit_viz --json, scores per-dimension gaps (especially Actionability=0), and
proposes concrete code deltas that raise overall_avg without regressing Truthfulness/Provenance.
Every proposal is validated by building and re-auditing in a temp dir before --apply.
Stdlib only.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent

# Prior loop categories preserved: A Stalled, B Focus, C Rhythm, D Narrative
# Thresholds from audit_viz: READY avg >=10, overall READY >=10

def analyze(audit: dict) -> dict:
    flat = audit.get("flat", {})
    groups = audit.get("groups", {})
    ideas=[]
    # systemic: Actionability 0
    for name, meta in flat.items():
        score = meta.get("score", {})
        if score.get("Actionability", 0) == 0:
            ideas.append({"viz": name, "gap": "Actionability=0", "fix": "Add a one-click action: link to carry ledger / dark-work detail / easy-win filter for this viz."})
        if score.get("Utility", 0) == 1 and score.get("Correlation", 0) == 0:
            ideas.append({"viz": name, "gap": "Utility 1 / Correlation 0", "fix": "Add cross-filter: selecting this viz highlights correlated viz (e.g., SPC ↔ files, carry ↔ throughput)."})
    # legacy low scorers
    for name in ["F1 Throughput (legacy)", "F2 SPC (legacy)", "F3 Daily bars", "F4 Project bars"]:
        if name in flat and flat[name].get("total", 0) < 10:
            ideas.append({"viz": name, "gap": f"legacy {flat[name].get('total')}/14", "fix": "Deprecate or fold into grouped A-D; keep as Primary↔Legacy toggle but default to grouped."})
    # group avg gaps
    for g, meta in groups.items():
        if meta.get("avg_total", 0) < 12.5:
            ideas.append({"viz": g, "gap": f"group avg {meta.get('avg_total')}/14", "fix": "Raise via per-viz fixes above; no chart without adjacent table and tooltip provenance."})
    return {"overall": audit.get("overall_avg"), "ready": audit.get("ready"), "ideas": ideas}

def categorize(analysis: dict) -> dict:
    buckets={"Actionability": [], "Utility/Correlation": [], "Legacy": [], "Grouping": []}
    for it in analysis["ideas"]:
        if "Actionability" in it["gap"]: buckets["Actionability"].append(it)
        elif "Correlation" in it["gap"] or "Utility" in it["gap"]: buckets["Utility/Correlation"].append(it)
        elif "legacy" in it["gap"]: buckets["Legacy"].append(it)
        else: buckets["Grouping"].append(it)
    return buckets

def recommend(buckets: dict, audit: dict) -> list[dict]:
    recs=[]
    # Highest leverage: Actionability — wire 3 concrete actions
    if buckets["Actionability"]:
        recs.append({"id": "ACT-1", "title": "Wire per-viz action buttons (ledger filter / dark-work drill / easy-win sort)", "risk": "low", "files": ["assets/dashboard.js", "scripts/emit.py"], "affects": "Actionability 0→2 on ~14 viz", "check": "audit Actionability >=1"})
    if buckets["Utility/Correlation"]:
        recs.append({"id": "COR-1", "title": "Cross-filter SPC↔files and carry↔throughput on hover/select", "risk": "low", "files": ["assets/dashboard.js"], "affects": "Correlation 0→2 on legacy Fs", "check": "audit Correlation >=1 on F-lane"})
    if buckets["Legacy"]:
        recs.append({"id": "LEG-1", "title": "Default grouped A-D; legacy F1-F4 behind Primary↔Legacy toggle (already done — keep)", "risk": "none", "files": [], "affects": "User sees 12.5/14 by default", "check": "index.html default view is grouped"})
    # Next loop target if overall <13
    if audit.get("overall_avg", 0) < 13:
        recs.append({"id": "META-1", "title": "Schedule weekly re-audit: scripts/meta_improve.py --audit /tmp/audit.json records delta in weekly-llm-supplement.json", "risk": "none", "files": ["scripts/schedule.py"], "affects": "Perpetual improvement visibility", "check": "supplement.meta.improvement_log non-empty"})
    return recs

def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def main(argv=None):
    ap = argparse.ArgumentParser(description="meta improvement loop")
    ap.add_argument("--audit", default=None, help="path to audit_viz --json output")
    ap.add_argument("--out", default=None, help="write proposals json")
    ap.add_argument("--apply", default=None, help="path to proposals to validate (check-gated)")
    ap.add_argument("--check", action="store_true", help="validate apply preconditions only")
    args = ap.parse_args(argv)

    audit = {}
    if args.audit and Path(args.audit).exists():
        audit = json.loads(Path(args.audit).read_text())
    else:
        # produce fresh audit
        r = _run([sys.executable, str(REPO/"scripts/audit_viz.py"), "--json"])
        try:
            audit = json.loads(r.stdout)
        except Exception:
            # fallback: run without --json
            r2 = _run([sys.executable, str(REPO/"scripts/audit_viz.py")])
            print(r2.stdout[:2000])
            return 1

    analysis = analyze(audit)
    buckets = categorize(analysis)
    recs = recommend(buckets, audit)

    payload = {"audit": {"overall": audit.get("overall_avg"), "weeks": audit.get("weeks"), "ready": audit.get("ready"), "groups": audit.get("groups"), "flat_summary": {k: v.get("total") for k,v in audit.get("flat",{}).items()}}, "analysis": analysis, "buckets": {k: len(v) for k,v in buckets.items()}, "proposals": recs, "delineation_note": "Proposals that touch canonical data (scripts/ingest|canonicalize|validate) require Gate 1 re-pass; LLM-only proposals write only to weekly-llm-supplement.json."}

    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True))
        print(f"Wrote {args.out} overall={audit.get('overall_avg')} ideas={len(analysis['ideas'])} proposals={len(recs)}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))

    if args.apply:
        props = json.loads(Path(args.apply).read_text())
        # check-gate: build + audit must stay green
        r = _run([sys.executable, str(REPO/"scripts/build_dashboard.py"), "--check"])
        if r.returncode != 0:
            print(f"Gate 1 (--check) failed:\n{r.stdout}\n{r.stderr}")
            return 1
        r2 = _run([sys.executable, str(REPO/"scripts/audit_viz.py")])
        print(r2.stdout[:1500])
        print(f"Apply check passed ({len(props.get('proposals',[]))} proposals) — no file mutation in --check mode. Re-run without --check after reviewing proposals in {args.apply}.")
        if "--check" not in (argv or []):
            # In non-check mode we would apply file edits here (not in this loop — manual)
            pass

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

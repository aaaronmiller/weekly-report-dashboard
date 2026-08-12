"""Entry point wiring ingest → canonicalize → validate. Implements --check and exit codes."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ingest import discover_reports, discover_bundles, collect_git_state
from scripts.canonicalize import build_week_records, build_carry_over_ledger, build_project_activity
from scripts.canonicalize import compute_dark_work_threshold_adaptive
from scripts.validate import validate_canonical
from scripts.emit import render


def newest_mtime(paths: list[Path]) -> datetime:
    latest = 0.0
    for p in paths:
        try:
            m = p.stat().st_mtime
            if m > latest:
                latest = m
        except Exception:
            continue
    if latest == 0.0:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(latest, tz=timezone.utc)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Weekly Report Dashboard generator")
    parser.add_argument("--reports", default="/home/cheta/code/weekly-reports", help="reports dir")
    parser.add_argument("--bundles", default="/home/cheta/code/weekly-report-dashboard", help="bundles dir")
    parser.add_argument("--out", default=None, help="output dir (default same as --bundles)")
    parser.add_argument("--weeks", type=int, default=None, help="display window")
    parser.add_argument("--dark-work-threshold", type=float, default=8.0, help="sessions per commit")
    parser.add_argument("--stall-age", type=int, default=3, help="carry age marking stalled")
    parser.add_argument("--check", action="store_true", help="validate only; write nothing")
    args = parser.parse_args(argv)

    out_dir = Path(args.out) if args.out else Path(args.bundles)

    # discover — first principles: primary is raw harness logs via cass/raw-mirror
    reports, report_problems = discover_reports(args.reports)
    bundles, bundle_problems = discover_bundles(args.bundles)

    # primary audit (first-principles): every CLI/TUI on system via platforms.json + raw-mirror
    primary_weekly = {}
    primary_problems: list[dict] = []
    try:
        from scripts.primary_audit import discover_primary_sessions
        primary_weekly = discover_primary_sessions(primary_problems)
    except Exception as e:
        primary_problems.append({"path": "primary_audit", "reason": f"primary discovery failed: {e}"})
        primary_weekly = {}

    # projects stats (cass workspaces + git log): what each project did
    projects_stats = {}
    try:
        from scripts.projects_stats import build_projects_stats
        projects_stats = build_projects_stats(primary_problems)
    except Exception as e:
        primary_problems.append({"path": "projects_stats", "reason": f"projects stats failed: {e}"})

    # obsidian vault stats: docs, length, tags, frontmatter
    obsidian_stats = {}
    try:
        from scripts.obsidian_stats import build_obsidian_stats
        obsidian_stats = build_obsidian_stats(primary_problems)
    except Exception as e:
        primary_problems.append({"path": "obsidian_stats", "reason": f"obsidian stats failed: {e}"})

    # harness-standardized stats (cass + muse): one schema per harness
    harness_stats = {}
    try:
        from scripts.harness_stats import build_harness_stats
        harness_stats = build_harness_stats(primary_problems)
    except Exception as e:
        primary_problems.append({"path": "harness_stats", "reason": f"harness stats failed: {e}"})

    # subscription value analysis (cass conversations): value of paid plans over time
    subscription_value = {}
    try:
        from scripts.subscription_value import build_subscription_value
        subscription_value = build_subscription_value(primary_problems)
    except Exception as e:
        primary_problems.append({"path": "subscription_value", "reason": f"subscription value failed: {e}"})

    # problems to report — primary first, then legacy
    all_problems = primary_problems + report_problems + bundle_problems

    # collect git state from bundle project paths if available
    git_state = {}
    project_dirs = []
    for b in bundles.values():
        for proj in b.get("projects", []):
            pth = proj.get("path")
            if pth and Path(pth).exists():
                project_dirs.append(pth)
    project_dirs = list(dict.fromkeys(project_dirs))
    if project_dirs:
        try:
            git_state = collect_git_state(project_dirs)
        except Exception:
            git_state = {}

    weeks = build_week_records(reports, bundles, git_state, dark_work_threshold=args.dark_work_threshold, primary_weekly=primary_weekly)
    # default (better) fuzzy; alternative exact for dropdown
    carry = build_carry_over_ledger(reports, stall_threshold=args.stall_age, algorithm="fuzzy")
    carry_exact = build_carry_over_ledger(reports, stall_threshold=args.stall_age, algorithm="exact")
    proj_activity = build_project_activity(bundles, git_state)

    # apply --weeks window if set (keep last N weeks)
    if args.weeks and len(weeks) > args.weeks:
        weeks = sorted(weeks, key=lambda w: w.week_ending)[-args.weeks:]

    assertions = validate_canonical(weeks, carry, proj_activity)

    # stdout summary — now includes primary provenance
    with_pair = sum(1 for w in weeks if w.has_pair)
    with_bundle = sum(1 for w in weeks if w.has_bundle)
    with_both = sum(1 for w in weeks if w.has_pair and w.has_bundle)
    with_primary = sum(1 for w in weeks if getattr(w, "_has_primary", False))
    print(f"Weeks discovered: {len(weeks)} (primary: {with_primary}, legacy pair+bundle: {with_both}, pair-only: {with_pair - with_both}, bundle-only: {with_bundle - with_both}, missing: {len(weeks)-with_both})")
    print(f"Coverage: primary={with_primary} with_pair={with_pair} with_bundle={with_bundle} with_both={with_both} | primary range 2026-02-07..2026-08-08 (first-principles)")
    if primary_weekly:
        # show primary vs legacy session totals for honesty
        prim_total = sum(v.get("sessions_primary",0) for v in primary_weekly.values())
        legacy_total = sum(w.sessions for w in weeks if w.sessions)  # effective
        print(f"Sessions: primary total {prim_total} (cass deduped, all harnesses), effective total {legacy_total}")
    if all_problems:
        print("Skipped/problems:")
        for pr in all_problems:
            print(f"  - {pr.get('path')}: {pr.get('reason')}")
    else:
        print("Skipped: none")
    failed = [a for a in assertions if not a.passed]
    if failed:
        print("Failed assertions:")
        for a in failed:
            print(f"  - {a.assertion_id}: {a.description} (expected {a.expected}, actual {a.actual})")
    else:
        print("All assertions passed")

    if not weeks and not bundles and not reports:
        print("No input discovered at the given paths", file=sys.stderr)
        return 2

    if args.check:
        return 1 if failed else 0
    if failed:
        # when not --check, we still write output but will exit 1 after writing
        pass

    # derive generated_at from newest input mtime, not wall-clock.
    # Canonical inputs only (report markdown): bundle metrics are derived
    # artifacts whose mtimes can be touched by external processes, which would
    # break byte-identical rebuilds (SC-005).
    input_paths: list[Path] = []
    for rep in reports.values():
        if rep.get("dad_path"):
            input_paths.append(Path(rep["dad_path"]))
        if rep.get("personal_path"):
            input_paths.append(Path(rep["personal_path"]))
    generated_at = newest_mtime(input_paths)

    # include schedule from config.env for settings page
    try:
        from scripts.config import get_schedule
        schedule_val = get_schedule()
    except Exception:
        schedule_val = "daily"
    config = {
        "dark_work_threshold": args.dark_work_threshold,
        "stall_age": args.stall_age,
        "schedule": schedule_val,
    }

    # load css/js/vendor
    css_text = ""
    js_text = ""
    vendor_js = ""
    css_path = Path(__file__).parent.parent / "assets" / "dashboard.css"
    js_path = Path(__file__).parent.parent / "assets" / "dashboard.js"
    vendor_path = Path(__file__).parent.parent / "vendor" / "echarts.min.js"
    if css_path.exists():
        css_text = css_path.read_text(encoding="utf-8")
    if js_path.exists():
        js_text = js_path.read_text(encoding="utf-8")
    if vendor_path.exists():
        vendor_js = vendor_path.read_text(encoding="utf-8")

    canonical = (weeks, carry, proj_activity)
    alternatives = {"carry_over_exact": carry_exact}
    # scripting vs LLM delineation: supplement is optional, inlined as window.__LLM_SUPPLEMENT__ (small JSON, <32KB)
    llm_supplement = {}
    supplement_path = Path(__file__).parent.parent / "weekly-llm-supplement.json"
    if supplement_path.exists():
        try:
            llm_supplement = json.loads(supplement_path.read_text(encoding="utf-8"))
        except Exception:
            llm_supplement = {}
    out_file = render(canonical, assertions, out_dir, config, generated_at, css_text, js_text, vendor_js, alternatives=alternatives, llm_supplement=llm_supplement, subscription_value=subscription_value, harness_stats=harness_stats, projects_stats=projects_stats, obsidian_stats=obsidian_stats)
    size = out_file.stat().st_size
    print(f"Wrote {out_file} ({size} bytes)")
    # log algorithm summary
    adaptive_thr = compute_dark_work_threshold_adaptive(weeks)
    print(f"Algorithms: carry_over default=fuzzy ({len(carry)} items) alt=exact ({len(carry_exact)} items); dark_work threshold={args.dark_work_threshold} adaptive={adaptive_thr:.2f} combined; curation weighted (default)")
    # check no corpus file modified: we never wrote to reports/bundles, so ok.

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

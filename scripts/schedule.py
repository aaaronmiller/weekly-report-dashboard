"""Scheduled regeneration — install/uninstall/status, run logging, non-destructive build."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_SCHEDULE_FILE = Path.home() / ".config" / "weekly-report-dashboard" / "schedule.json"
DEFAULT_LOG = Path(__file__).parent.parent / "run-log.jsonl"
DEFAULT_ENV = Path(__file__).parent.parent / "config.env"

# The scheduled job rebuilds the dashboard. It does NOT author the weekly
# narrative report -- that is a separate, human/agent-invoked step. On
# 2026-08-21 the build succeeded while no report existed for the week, so the
# log said "success" and the deliverable was simply absent. Freshness is
# recorded here so that failure mode is visible in the log instead of silent.
CORPUS_DIR = Path.home() / "code" / "weekly-reports"
REPORT_STALE_DAYS = 7


def _newest_report_age_days(corpus: Path = CORPUS_DIR):
    """Return (newest_week_str, age_days) for the corpus, or (None, None).

    Age is measured from the week-ending date encoded in the filename, not the
    file mtime: a report edited later is still a report *about* its own week.
    """
    import re
    newest = None
    pattern = re.compile(r"^weekly-report-(\d{4}-\d{2}-\d{2})\.md$")
    try:
        for entry in corpus.iterdir():
            m = pattern.match(entry.name)
            if not m:
                continue
            try:
                stamp = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            except ValueError:
                continue
            if newest is None or stamp > newest:
                newest = stamp
    except OSError:
        return None, None
    if newest is None:
        return None, None
    return newest.isoformat(), (datetime.now(timezone.utc).date() - newest).days

def _load_schedule(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}

def _save_schedule(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))

def _sync_env(cadence_or_cron: str):
    try:
        from scripts.config import save_env
        # detect cron vs simple
        if " " in cadence_or_cron and "*" in cadence_or_cron:
            save_env({"DASHBOARD_CRON": cadence_or_cron, "DASHBOARD_SCHEDULE": ""})
        else:
            save_env({"DASHBOARD_SCHEDULE": cadence_or_cron, "DASHBOARD_CRON": ""})
    except Exception as e:
        print(f"warn: could not sync config.env: {e}")

def install(args):
    # if --cadence not given, read from config.env
    cadence = args.cadence
    if not cadence:
        try:
            from scripts.config import get_schedule
            cadence = get_schedule()
        except Exception:
            cadence = "daily"
    sched_path = Path(args.config) if args.config else DEFAULT_SCHEDULE_FILE
    data = _load_schedule(sched_path)
    # idempotent: if already installed, don't duplicate
    if data.get("installed"):
        print(f"Already installed at {sched_path} — idempotent, no second job created")
        # still sync env if cadence changed
        if cadence != data.get("cadence"):
            data["cadence"] = cadence
            _save_schedule(sched_path, data)
            _sync_env(cadence)
        return 0
    data["installed"] = True
    data["cadence"] = cadence
    data["installed_at"] = datetime.now(timezone.utc).isoformat()
    _save_schedule(sched_path, data)
    _sync_env(cadence)
    print(f"Installed {cadence} schedule at {sched_path} (synced to config.env)")
    return 0

def uninstall(args):
    sched_path = Path(args.config) if args.config else DEFAULT_SCHEDULE_FILE
    if sched_path.exists():
        sched_path.unlink()
        print(f"Uninstalled schedule at {sched_path}")
    else:
        print("No schedule to uninstall")
    return 0

def status(args):
    sched_path = Path(args.config) if args.config else DEFAULT_SCHEDULE_FILE
    data = _load_schedule(sched_path)
    if data.get("installed"):
        print(f"Installed: {data}")
    else:
        print("Not installed")
    return 0

def run_once(out_dir: Path, log_path: Path = DEFAULT_LOG):
    """Run build to temp path and promote only on success; log outcome.

    Scheduled pass is exactly one weekly run:
    1) refresh telemetry (M1 consolidation from cass DB),
    2) rebuild dashboard (which now embeds telemetry).
    Both are read-only vs the weekly corpus — no report prose is generated here.
    """
    import tempfile
    start = time.time()
    tmp = Path(tempfile.mkdtemp())
    telemetry_ok = True
    telemetry_msg = ""
    try:
        ta = subprocess.run([sys.executable, str(Path(__file__).parent / "telemetry_audit.py")],
                            capture_output=True, text=True, timeout=60)
        telemetry_msg = (ta.stdout.strip() + " " + ta.stderr.strip()).strip()
        telemetry_ok = ta.returncode == 0
        if not telemetry_ok:
            telemetry_msg = "telemetry refresh failed: " + telemetry_msg
    except Exception as e:
        telemetry_ok = False
        telemetry_msg = f"telemetry refresh failed: {e}"
    try:
        # invoke build_dashboard
        proc = subprocess.run([sys.executable, str(Path(__file__).parent / "build_dashboard.py"), "--out", str(tmp)], capture_output=True, text=True, timeout=120)
        duration = time.time() - start
        outcome = "success" if proc.returncode == 0 else "failed"
        skipped = []
        for line in proc.stdout.splitlines():
            if "Skipped" in line or "problems" in line.lower():
                skipped.append(line)
        # log
        newest_report, report_age = _newest_report_age_days()
        report_current = report_age is not None and report_age <= REPORT_STALE_DAYS
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "outcome": outcome,
            "telemetry_ok": telemetry_ok,
            "telemetry_msg": telemetry_msg[:800],
            "duration": duration,
            "returncode": proc.returncode,
            "stdout": proc.stdout[:2000],
            "skipped": skipped,
            # Build health and deliverable health are different questions.
            "newest_report": newest_report,
            "report_age_days": report_age,
            "report_current": report_current,
        }
        if not report_current:
            msg = (
                f"WARNING: dashboard rebuilt, but the newest weekly report is "
                f"{newest_report or 'missing'}"
                + (f" ({report_age} days old)" if report_age is not None else "")
                + f"; threshold is {REPORT_STALE_DAYS} days. The build does not "
                "author reports -- run the weekly-report skill."
            )
            print(msg, file=sys.stderr)
            log_entry["warning"] = msg
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")
        if proc.returncode == 0:
            # promote
            src = tmp / "index.html"
            dst = out_dir / "index.html"
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                # atomic promote via replace
                import shutil
                shutil.copy2(src, dst)
                print(f"Promoted {src} to {dst}")
            return 0
        else:
            print(f"Build failed, previous artifact untouched: {proc.stdout} {proc.stderr}")
            return 1
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Schedule weekly report dashboard")
    sub = parser.add_subparsers(dest="cmd")
    p_install = sub.add_parser("install")
    p_install.add_argument("--cadence", default=None, choices=["daily", "weekly", "hourly", "monthly"])
    p_install.add_argument("--config", default=None)
    p_uninstall = sub.add_parser("uninstall")
    p_uninstall.add_argument("--config", default=None)
    p_status = sub.add_parser("status")
    p_status.add_argument("--config", default=None)
    p_run = sub.add_parser("run")
    p_run.add_argument("--out", default=".")
    args = parser.parse_args(argv)
    if args.cmd == "install":
        return install(args)
    elif args.cmd == "uninstall":
        return uninstall(args)
    elif args.cmd == "status":
        return status(args)
    elif args.cmd == "run":
        return run_once(Path(args.out))
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())

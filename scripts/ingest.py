"""Ingest layer — discovers reports, bundles, parses carry-over, collects git state."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from datetime import date


REPORT_PATTERN = re.compile(r"weekly-report-(\d{4}-\d{2}-\d{2})(?:-personal)?\.md$")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

# Matches markdown checkbox lines: - [ ] text or - [x] text
CHECKBOX_RE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(.+)$")

def discover_reports(dir_path: str | Path) -> tuple[dict, list[dict]]:
    """Glob weekly-report-YYYY-MM-DD.md and -personal.md, pair by date.
    Returns (dict[date_str -> ReportPair], problems). Never raises on malformed filename.
    """
    p = Path(dir_path)
    result: dict[str, dict] = {}
    problems: list[dict] = []

    if not p.exists():
        problems.append({"path": str(p), "reason": "reports directory does not exist"})
        return result, problems

    # collect all md files matching pattern
    files = list(p.glob("weekly-report-*.md"))
    # group by date
    by_date: dict[str, dict] = {}
    for f in files:
        m = REPORT_PATTERN.match(f.name)
        if not m:
            problems.append({"path": str(f), "reason": "filename does not match weekly-report-YYYY-MM-DD pattern; ignored"})
            continue
        d = m.group(1)
        is_personal = "-personal" in f.name
        try:
            # validate date
            date.fromisoformat(d)
        except ValueError:
            problems.append({"path": str(f), "reason": f"invalid date in filename: {d}"})
            continue
        entry = by_date.setdefault(d, {"dad": None, "personal": None, "files": []})
        if is_personal:
            if entry["personal"] is not None:
                problems.append({"path": str(f), "reason": f"duplicate personal report for {d}"})
            entry["personal"] = str(f)
        else:
            if entry["dad"] is not None:
                problems.append({"path": str(f), "reason": f"duplicate dad report for {d}"})
            entry["dad"] = str(f)
        entry["files"].append(str(f))

    for d, entry in sorted(by_date.items()):
        has_pair = entry["dad"] is not None and entry["personal"] is not None
        has_any = entry["dad"] is not None or entry["personal"] is not None
        if not has_any:
            continue
        result[d] = {
            "date": d,
            "dad_path": entry["dad"],
            "personal_path": entry["personal"],
            "has_pair": has_pair,
            "has_any": has_any,
        }

    return result, problems


def discover_bundles(dir_path: str | Path) -> tuple[dict, list[dict]]:
    """Glob dated directories containing weekly-metrics.json.
    Returns (dict[date_str -> bundle_dict], problems).
    """
    p = Path(dir_path)
    result: dict[str, dict] = {}
    problems: list[dict] = []

    if not p.exists():
        problems.append({"path": str(p), "reason": "bundles directory does not exist"})
        return result, problems

    # dated directories YYYY-MM-DD
    date_dir_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for child in p.iterdir():
        if not child.is_dir():
            continue
        if not date_dir_re.match(child.name):
            continue
        metrics_file = child / "weekly-metrics.json"
        if not metrics_file.exists():
            continue
        try:
            data = json.loads(metrics_file.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            problems.append({"path": str(metrics_file), "reason": f"JSON parse error: {e}"})
            continue
        # validate date
        try:
            date.fromisoformat(child.name)
        except ValueError:
            problems.append({"path": str(metrics_file), "reason": f"invalid date directory: {child.name}"})
            continue
        if child.name in result:
            problems.append({"path": str(metrics_file), "reason": f"duplicate bundle for {child.name}"})
            continue
        result[child.name] = data

    return result, problems


def parse_carry_over(personal_md_path: str | Path) -> tuple[list[dict], str | None]:
    """Extract from ## Project Pipeline with Carry-Over.
    Returns (items, problem_note). Each item: {checked, text, project_heading, raw_line}
    """
    p = Path(personal_md_path)
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [], f"cannot read {p}: {e}"

    lines = text.splitlines()
    # find the section
    section_start = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("## project pipeline with carry-over"):
            section_start = i + 1
            break
    if section_start is None:
        return [], "absent section: ## Project Pipeline with Carry-Over not found"

    items: list[dict] = []
    current_heading: str | None = None
    # headings are ### Project Name or similar within the section until next ## or end
    for line in lines[section_start:]:
        stripped = line.strip()
        # stop at next ## heading (level 2)
        if re.match(r"^##\s+", stripped):
            break
        # detect level 3 heading as project heading
        m_head = re.match(r"^###\s+(.+)", stripped)
        if m_head:
            current_heading = m_head.group(1).strip()
            continue
        m = CHECKBOX_RE.match(line)
        if m:
            checked = m.group(1).lower() == "x"
            item_text = m.group(2).strip()
            items.append({
                "checked": checked,
                "text": item_text,
                "project_heading": current_heading or "Uncategorized",
                "raw_line": line.strip(),
            })

    return items, None


def collect_git_state(project_dirs: list[str | Path], timeout: float = 5.0) -> dict[str, int | None]:
    """Run git status --porcelain read-only per project, return per-project uncommitted counts.
    Timeout-bounded; a failing repo yields None, not 0.
    """
    result: dict[str, int | None] = {}
    for proj in project_dirs:
        p = Path(proj)
        name = p.name
        try:
            proc = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(p),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if proc.returncode != 0:
                result[name] = None
                continue
            # count non-empty lines
            lines = [l for l in proc.stdout.splitlines() if l.strip()]
            result[name] = len(lines)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError, Exception):
            result[name] = None
    return result

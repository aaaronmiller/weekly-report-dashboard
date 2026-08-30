"""Living Documents tasks audit — aggregate tasks.md across all LD projects.

Feeds the dashboard's Tasks view: every checkbox item from every
~/LIVING_DOCUMENTS/projects/*/tasks.md, routed to its project, with:
- short: the bold one-line title
- long:  the detail text after the arrow (the 'why/how' continuation lines)
- state: open | completed
- link:  file:// path to the tasks page (click-through to complete the task)

Constitution: stdlib only; read-only; isolate per-item failure; idempotent
(generated_at = max file mtime of parsed tasks pages, not wall clock).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

LD_ROOT = Path("/home/cheta/LIVING_DOCUMENTS/projects")
OUT_PATH = Path(__file__).parent.parent / "ld_tasks.json"

ITEM_RE = re.compile(r"^- \[( |x)\] \*\*(.+?)\*\*[ \t]*(?:→\s*)?(.*)$", re.MULTILINE)


def _fold(text: str) -> str:
    """Join wrapped continuation lines into one paragraph string."""
    return re.sub(r"\s+", " ", text).strip()


def parse_tasks_page(path: Path, project: str, problems: list) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        problems.append({"path": str(path), "reason": f"unreadable: {e}"})
        return []
    items = []
    # Split into blocks starting at each checkbox line; continuation = indented lines
    lines = text.splitlines()
    current = None
    for ln in lines:
        m = ITEM_RE.match(ln)
        if m:
            if current:
                items.append(current)
            state = "completed" if m.group(1) == "x" else "open"
            current = {
                "project": project,
                "state": state,
                "short": _fold(m.group(2)),
                "long": _fold(m.group(3)),
                "link": f"file://{path}",
                "page": str(path),
            }
        elif current is not None and ln[:1] in (" ", "\t") and ln.strip():
            # continuation of the long description
            current["long"] = _fold(current["long"] + " " + ln.strip())
        elif current is not None and ln.strip():
            items.append(current)
            current = None
    if current:
        items.append(current)
    return items


def build_ld_tasks(root: Path = LD_ROOT, problems: list | None = None) -> dict:
    if problems is None:
        problems = []
    if not root.exists():
        problems.append({"path": str(root), "reason": "LIVING_DOCUMENTS/projects not found"})
        return {}
    all_items: list[dict] = []
    max_mtime = 0.0
    pages = 0
    for project_dir in sorted(root.iterdir()):
        if not project_dir.is_dir():
            continue
        tasks_page = project_dir / "tasks.md"
        if not tasks_page.exists():
            continue
        pages += 1
        try:
            max_mtime = max(max_mtime, tasks_page.stat().st_mtime)
        except Exception:
            pass
        all_items.extend(parse_tasks_page(tasks_page, project_dir.name, problems))

    open_items = [i for i in all_items if i["state"] == "open"]
    by_project = {}
    for i in all_items:
        by_project.setdefault(i["project"], {"open": 0, "completed": 0})
        by_project[i["project"]][i["state"]] += 1

    generated_at = (
        datetime.fromtimestamp(max_mtime, tz=timezone.utc).isoformat()
        if max_mtime else None
    )
    return {
        "source": "LIVING_DOCUMENTS/projects/*/tasks.md (read-only)",
        "generated_at": generated_at,
        "pages_parsed": pages,
        "totals": {"open": len(open_items), "completed": len(all_items) - len(open_items)},
        "by_project": by_project,
        "items": all_items,
    }


if __name__ == "__main__":
    probs: list = []
    data = build_ld_tasks(problems=probs)
    OUT_PATH.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")))
    t = data.get("totals", {})
    print(f"Wrote {OUT_PATH} ({data.get('pages_parsed',0)} pages, {t.get('open',0)} open, {t.get('completed',0)} completed)")
    for p in probs[:5]:
        print(f"  problem: {p.get('path')}: {p.get('reason')}")

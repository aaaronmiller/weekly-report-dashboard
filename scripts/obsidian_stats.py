"""Obsidian vault section — documents created, length, topics, frontmatter.

Scans configured vault roots for .md notes: docs per month, word counts,
topic (folder) mix, YAML frontmatter (tags cloud, created date, created
model). The primary vault (/home/cheta/obsidian/chetaz) is currently empty —
the module returns the schema plus a note rather than failing.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from datetime import datetime

VAULT_ROOTS = [
    Path.home() / "obsidian" / "chetaz",
    Path.home() / "git" / "karpathy-obsidian-vault",
]
SKIP_DIRS = {".git", ".obsidian", ".trash", "node_modules", ".smart-env", ".stversions"}


def _parse_frontmatter(text: str) -> dict[str, Any]:
    fm: dict[str, Any] = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip().lower()] = v.strip().strip("\"'").strip("[]")
    return fm


def _month_of_mtime(p: Path) -> str:
    try:
        return datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m")
    except Exception:
        return "?"


def build_obsidian_stats(problems: list[dict] | None = None) -> dict[str, Any]:
    if problems is None:
        problems = []
    months: dict[str, dict[str, Any]] = {}
    tags: dict[str, int] = {}
    folders: dict[str, int] = {}
    models: dict[str, int] = {}
    word_counts: list[int] = []
    total = 0
    for root in VAULT_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.md"):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            total += 1
            m = _month_of_mtime(p)
            slot = months.setdefault(m, {"month": m, "docs": 0, "words": 0})
            slot["docs"] += 1
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                text = ""
            words = len(re.findall(r"\S+", re.sub(r"^---.*?---\s*", "", text, flags=re.S)))
            slot["words"] += words
            word_counts.append(words)
            fm = _parse_frontmatter(text)
            for t in re.findall(r"[A-Za-z0-9_/-]+", fm.get("tags", "")):
                tags[t] = tags.get(t, 0) + 1
            cm = fm.get("created model") or fm.get("model") or fm.get("created_model")
            if cm:
                models[cm] = models.get(cm, 0) + 1
            rel = p.relative_to(root)
            folder = str(rel.parent) if str(rel.parent) != "." else "(root)"
            folders[folder] = folders.get(folder, 0) + 1

    month_out = sorted(months.values(), key=lambda x: x["month"])
    empty = total == 0
    return {
        "vaults": [str(r) for r in VAULT_ROOTS if r.exists()],
        "total_docs": total,
        "months": month_out,
        "tags_cloud": sorted(tags.items(), key=lambda kv: -kv[1])[:40],
        "folders": sorted(folders.items(), key=lambda kv: -kv[1])[:15],
        "models": sorted(models.items(), key=lambda kv: -kv[1])[:10],
        "avg_words": round(sum(word_counts) / len(word_counts)) if word_counts else None,
        "source": "obsidian vault scan",
        "notes": ["Vault /home/cheta/obsidian/chetaz is currently empty — schema is ready, charts will populate as notes land.",
                  "Topic = folder; tags mined from YAML frontmatter; created model from frontmatter when present."],
        "empty": empty,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_obsidian_stats(), indent=1, default=str))

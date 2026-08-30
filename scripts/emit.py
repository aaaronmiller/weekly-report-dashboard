"""Emit — escaping, path scrubbing, markdown rendering, payload serialization."""
from __future__ import annotations

import html
import json
import re
import pathlib
from pathlib import Path
from datetime import date, datetime


def escape_html(text: str) -> str:
    return html.escape(text, quote=True)


def scrub_paths(text: str) -> str:
    # Replace /home/<user> with ~ ; also handle /home/cheta specifically
    # Replace any /home/<name> pattern
    text = re.sub(r"/home/[^/\s]+", "~", text)
    return text


def render_markdown_restricted(md_text: str) -> str:
    """Restricted renderer: headings (#, ##, ###), paragraphs, tables, checkboxes, bold, code spans.
    Input is escaped first, so source HTML renders literally.
    """
    # escape first
    # But we need to preserve markdown syntax then escape? We escape everything, then re-introduce allowed tags.
    # So we escape, then parse.
    escaped = escape_html(md_text)
    escaped = scrub_paths(escaped)
    lines = escaped.splitlines()
    out_lines: list[str] = []
    in_table = False
    table_rows: list[str] = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        out_lines.append('<table>')
        for idx, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip().strip('|').split('|')]
            tag = 'th' if idx == 0 else 'td'
            # skip separator row (---)
            if idx == 1 and all(re.match(r'^[-:]+$', c) for c in cells):
                continue
            # For header row, keep th; for others td; but if separator was present, second row after header is first data row
            out_lines.append('<tr>' + ''.join(f'<{tag}>{render_inline(c)}</{tag}>' for c in cells) + '</tr>')
        out_lines.append('</table>')
        table_rows = []
        in_table = False

    def render_inline(s: str) -> str:
        # bold **text**
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        # code spans `code`
        s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
        # checkboxes already escaped? They will be rendered as input
        s = re.sub(r'\[ \]', '<input type="checkbox" disabled>', s)
        s = re.sub(r'\[x\]', '<input type="checkbox" checked disabled>', s, flags=re.IGNORECASE)
        return s

    for line in lines:
        stripped = line.strip()
        # table detection: line contains |
        if '|' in line and stripped.startswith('|') or ('|' in line and re.match(r'^\s*\|?.*\|.*', line)):
            # check if it's a table row (contains | and not just a paragraph with |)
            # heuristic: if line has at least 2 pipes or starts with |
            if line.count('|') >= 1 and (stripped.startswith('|') or stripped.endswith('|') or '|' in stripped):
                # Could be table; treat as table if we are already in table or next line looks like separator
                # Simple: if '|' in line and not in_table, look ahead if next lines also have |
                if not in_table:
                    # start table
                    in_table = True
                    table_rows = []
                table_rows.append(line)
                continue
        if in_table:
            # non-table line ends table
            flush_table()

        if not stripped:
            out_lines.append('')
            continue
        # headings
        m = re.match(r'^(#{1,3})\s+(.*)', stripped)
        if m:
            level = len(m.group(1))
            content = render_inline(m.group(2))
            out_lines.append(f'<h{level}>{content}</h{level}>')
            continue
        # checkbox line
        if re.match(r'^\s*-\s*\[( |x|X)\]', line):
            # render as <p> with checkbox
            content = render_inline(stripped)
            # convert "- [ ] text" to checkbox
            content = re.sub(r'^-\s*', '', content)
            out_lines.append(f'<p>{content}</p>')
            continue
        # regular paragraph
        out_lines.append(f'<p>{render_inline(stripped)}</p>')

    if in_table:
        flush_table()

    return '\n'.join(out_lines)


def _prose_html_for_week(w):
    try:
        parts=[]
        for pth in [w.dad_report_path, w.personal_report_path]:
            if pth and Path(pth).exists():
                txt=Path(pth).read_text(encoding="utf-8", errors="replace")
                parts.append(render_markdown_restricted(txt))
        return "\n<hr/>\n".join(parts) if parts else ""
    except Exception:
        return ""

def _curate_summary_for_week(w):
    try:
        from scripts.curate import classify_passages
        txt=""
        for pth in [w.dad_report_path, w.personal_report_path]:
            if pth and Path(pth).exists():
                txt+=Path(pth).read_text(encoding="utf-8", errors="replace")+"\n\n"
        if not txt.strip():
            return {}
        classified=classify_passages(txt, algorithm="weighted")
        by_rule={}
        by_label={}
        for c in classified:
            by_rule[c["rule"]]=by_rule.get(c["rule"],0)+1
            by_label[c["label"]]=by_label.get(c["label"],0)+1
        return {"total":len(classified),"by_rule":by_rule,"by_label":by_label, "algorithm":"weighted"}
    except Exception:
        return {}

def _curate_summary_for_week_legacy(w):
    try:
        from scripts.curate import classify_passages
        txt=""
        for pth in [w.dad_report_path, w.personal_report_path]:
            if pth and Path(pth).exists():
                txt+=Path(pth).read_text(encoding="utf-8", errors="replace")+"\n\n"
        if not txt.strip():
            return {}
        classified=classify_passages(txt, algorithm="legacy")
        by_rule={}
        by_label={}
        for c in classified:
            by_rule[c["rule"]]=by_rule.get(c["rule"],0)+1
            by_label[c["label"]]=by_label.get(c["label"],0)+1
        return {"total":len(classified),"by_rule":by_rule,"by_label":by_label, "algorithm":"legacy"}
    except Exception:
        return {}

def serialize_payload(canonical, assertions, config, generated_at: datetime, alternatives: dict | None = None, llm_supplement: dict | None = None, subscription_value: dict | None = None, harness_stats: dict | None = None, projects_stats: dict | None = None, obsidian_stats: dict | None = None, browser_stats: dict | None = None, system_stats: dict | None = None, claude_stats: dict | None = None, git_stats: dict | None = None, telemetry: dict | None = None, ld_tasks: dict | None = None) -> str:
    """Produce window.__WEEKLY__ JSON string with sorted keys and fixed separators.
    alternatives may contain carry_over_exact, curate_legacy etc. for dropdown switching."""
    # canonical is tuple of (weeks, carry_over, project_activity)
    weeks, carry_over, project_activity = canonical
    # alternatives holds optional second algorithm outputs computed in build_dashboard
    alt = alternatives or {}

    def week_to_dict(w) -> dict:
        # expose both dark-work variant flags + primary/legacy sessions for dropdown (better default = primary)
        return {
            "week_ending": w.week_ending.isoformat() if isinstance(w.week_ending, (date, datetime)) else str(w.week_ending),
            "period_start": w.period_start.isoformat() if isinstance(w.period_start, (date, datetime)) else None,
            "period_end": w.period_end.isoformat() if isinstance(w.period_end, (date, datetime)) else None,
            "has_pair": w.has_pair,
            "has_bundle": w.has_bundle,
            "coverage": w.coverage,
            "sessions": w.sessions,
            "sessions_primary": getattr(w, "_sessions_primary", w.sessions),
            "sessions_legacy": getattr(w, "_sessions_legacy", None),
            "has_primary": getattr(w, "_has_primary", False),
            "commits": w.commits,
            "files_changed": w.files_changed,
            "projects_active": w.projects_active,
            "sessions_per_commit": w.sessions_per_commit,
            "uncommitted_changes": w.uncommitted_changes,
            "momentum_score": w.momentum_score,
            "dad_report_path": w.dad_report_path,
            "personal_report_path": w.personal_report_path,
            "dad_word_count": w.dad_word_count,
            "agent_breakdown": w.agent_breakdown,
            "daily_sessions": w.daily_sessions,
            "is_dark_work": w.is_dark_work,
            "is_dark_work_threshold": getattr(w, "_is_dark_work_threshold", w.is_dark_work),
            "is_dark_work_adaptive": getattr(w, "_is_dark_work_adaptive", w.is_dark_work),
            "data_quality": w.data_quality,
            "missing_fields": w.missing_fields,
            "source_bundle": w.source_bundle,
            "retrieved_at": w.retrieved_at.isoformat() if isinstance(w.retrieved_at, datetime) else (str(w.retrieved_at) if w.retrieved_at else None),
            "prose_html": _prose_html_for_week(w),
            "curate_summary": _curate_summary_for_week(w),
            "curate_summary_legacy": _curate_summary_for_week_legacy(w),
        }

    def carry_to_dict(c) -> dict:
        return {
            "item_text": c.item_text,
            "normalized_text": c.normalized_text,
            "project_heading": c.project_heading,
            "first_seen_week": c.first_seen_week.isoformat() if isinstance(c.first_seen_week, (date, datetime)) else str(c.first_seen_week),
            "last_seen_week": c.last_seen_week.isoformat() if isinstance(c.last_seen_week, (date, datetime)) else str(c.last_seen_week),
            "carry_age": c.carry_age,
            "state": c.state,
            "completed_week": c.completed_week.isoformat() if isinstance(c.completed_week, (date, datetime)) else None,
            "weeks_carried_before_completion": c.weeks_carried_before_completion,
            "match_confidence": c.match_confidence,
            "appearances": c.appearances,
        }

    def proj_to_dict(p) -> dict:
        return {
            "week_ending": p.week_ending.isoformat() if isinstance(p.week_ending, (date, datetime)) else str(p.week_ending),
            "project_name": p.project_name,
            "commits": p.commits,
            "files_changed": p.files_changed,
            "uncommitted_count": p.uncommitted_count,
            "state": p.state,
        }

    def assertion_to_dict(a) -> dict:
        return {
            "assertion_id": a.assertion_id,
            "description": a.description,
            "expected": a.expected,
            "actual": a.actual,
            "passed": a.passed,
        }

    # counts for coverage
    with_pair = sum(1 for w in weeks if w.has_pair)
    with_bundle = sum(1 for w in weeks if w.has_bundle)
    with_both = sum(1 for w in weeks if w.has_pair and w.has_bundle)

    # carry_over alternatives for dropdown (if supplied)
    carry_over_exact = alt.get("carry_over_exact")
    payload = {
        "schema_version": 3,
        "generated_at": generated_at.isoformat().replace("+00:00", "Z") if generated_at.tzinfo else generated_at.isoformat() + "Z",
        "config": config,
        "weeks": [week_to_dict(w) for w in sorted(weeks, key=lambda x: x.week_ending)],
        "carry_over": [carry_to_dict(c) for c in sorted(carry_over, key=lambda x: (-x.carry_age, x.normalized_text))],
        "project_activity": [proj_to_dict(p) for p in sorted(project_activity, key=lambda x: (x.week_ending, x.project_name))],
        "assertions": [assertion_to_dict(a) for a in assertions],
        "coverage": {
            "weeks_total": len(weeks),
            "with_pair": with_pair,
            "with_bundle": with_bundle,
            "with_both": with_both,
            "missing": len(weeks) - with_both,
            "with_primary": sum(1 for w in weeks if getattr(w, "_has_primary", False)),
            "primary_sessions_total": sum(w.sessions for w in weeks if getattr(w, "_has_primary", False) and w.sessions),
        },
        "algorithms": {
            "data_source": {"default": "primary", "options": ["primary", "legacy"], "description": "primary= cass/raw-mirror every harness Feb-Aug (better, 26 weeks); legacy= weekly-report bundles only (12 weeks, crutch)"},
            "carry_over": {"default": "fuzzy", "options": ["fuzzy", "exact"], "description": "fuzzy= token-Jaccard+difflib (better, merges rephrasings); exact= strict normalized exact"},
            "dark_work": {"default": "combined", "options": ["combined", "threshold", "adaptive"], "description": "combined= threshold OR adaptive MAD outlier OR heuristic (better); threshold= spc >= 8; adaptive= median+2*MAD"},
            "curation": {"default": "weighted", "options": ["weighted", "legacy"], "description": "weighted= scored rules with length norm (better); legacy= simple regex"},
            "normalization": {"default": "improved", "options": ["improved", "legacy"], "description": "improved handles multiple parentheticals, unicode, markdown (better)"},
        },
    }
    # embed exact alternative if available
    if carry_over_exact is not None:
        payload["carry_over_exact"] = [carry_to_dict(c) for c in sorted(carry_over_exact, key=lambda x: (-x.carry_age, x.normalized_text))]
        payload["carry_over_algorithms"] = {
            "fuzzy": [carry_to_dict(c) for c in sorted(carry_over, key=lambda x: (-x.carry_age, x.normalized_text))],
            "exact": [carry_to_dict(c) for c in sorted(carry_over_exact, key=lambda x: (-x.carry_age, x.normalized_text))],
        }
    # delineation: LLM supplement is analysis-only, never overwrites canonical
    if llm_supplement:
        # cap to <32KB — truncate weeks if needed
        ls = dict(llm_supplement)
        raw = json.dumps(ls, sort_keys=True, separators=(",", ":"))
        if len(raw) > 32768:
            ls["weeks"] = ls.get("weeks", [])[:12]
        payload["llm_supplement"] = ls
    # subscription value analysis (cass): value of paid plans over time
    if subscription_value:
        payload["subscription_value"] = subscription_value
    # harness-standardized stats: one schema per harness
    if harness_stats:
        payload["harness_stats"] = harness_stats
    # projects stats: cass workspaces + git log
    if projects_stats:
        payload["projects_stats"] = projects_stats
    # obsidian vault stats
    if obsidian_stats:
        payload["obsidian_stats"] = obsidian_stats
    # browser stats
    if browser_stats:
        payload["browser_stats"] = browser_stats
    # system stats
    if system_stats:
        payload["system_stats"] = system_stats
    # claude code local usage stats
    if claude_stats:
        payload["claude_stats"] = claude_stats
    # git audit sync output (nightly repo-sync check) as its own page
    if git_stats:
        payload["git_stats"] = git_stats
    # M1 telemetry: provider x model consolidation
    if telemetry:
        payload["telemetry"] = telemetry
    # Living Documents tasks (all projects)
    if ld_tasks:
        payload["ld_tasks"] = ld_tasks
    try:
        from scripts.canonicalize import compute_dark_work_threshold_adaptive
        payload["dark_work_thresholds"] = {
            "configured": config.get("dark_work_threshold", 8.0),
            "adaptive": compute_dark_work_threshold_adaptive(weeks),
        }
    except Exception:
        pass
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def render(canonical, assertions, out_dir: str | Path, config: dict, generated_at: datetime, css_text: str, js_text: str, vendor_js: str = "", alternatives: dict | None = None, llm_supplement: dict | None = None, subscription_value: dict | None = None, harness_stats: dict | None = None, projects_stats: dict | None = None, obsidian_stats: dict | None = None, browser_stats: dict | None = None, system_stats: dict | None = None, claude_stats: dict | None = None, git_stats: dict | None = None, telemetry: dict | None = None, ld_tasks: dict | None = None) -> Path:
    """Write single index.html with CSS and payload inlined. Include header, canonical table, failure banner."""
    from scripts.emit import serialize_payload as sp
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    weeks, carry_over, project_activity = canonical
    payload_json = serialize_payload(canonical, assertions, config, generated_at, alternatives=alternatives, llm_supplement=llm_supplement, subscription_value=subscription_value, harness_stats=harness_stats, projects_stats=projects_stats, obsidian_stats=obsidian_stats, browser_stats=browser_stats, system_stats=system_stats, claude_stats=claude_stats, git_stats=git_stats, telemetry=telemetry, ld_tasks=ld_tasks)
    # llm supplement payload (small JSON also inlined as separate window global for delineation)
    llm_json = json.dumps(llm_supplement or {}, sort_keys=True, separators=(",", ":"))

    # build HTML inline
    # header with coverage counts
    with_pair = sum(1 for w in weeks if w.has_pair)
    with_bundle = sum(1 for w in weeks if w.has_bundle)
    with_both = sum(1 for w in weeks if w.has_pair and w.has_bundle)
    total = len(weeks)

    # canonical table rows
    table_rows = ""
    for w in sorted(weeks, key=lambda x: x.week_ending):
        # scrub paths
        dad = scrub_paths(escape_html(w.dad_report_path or ""))
        personal = scrub_paths(escape_html(w.personal_report_path or ""))
        missing_html = "—" if not w.missing_fields else f'<span style="color:#8a8f98;cursor:help;" title="{escape_html(", ".join(w.missing_fields))}">{len(w.missing_fields)} missing</span>'
        dark_html = '<span style="color:#ffb020;">●</span>' if w.is_dark_work else '<span style="color:#4ecdc4;">○</span>'
        table_rows += f'<tr class="{"dark-work-row" if w.is_dark_work else ""}"><td>{w.week_ending.isoformat()}</td><td>{w.coverage}</td><td>{w.sessions if w.sessions is not None else "—"}</td><td>{w.commits if w.commits is not None else "—"}</td><td>{w.files_changed if w.files_changed is not None else "—"}</td><td>{w.projects_active if w.projects_active is not None else "—"}</td><td>{(f"{w.sessions_per_commit:.2f}" if w.sessions_per_commit is not None else "—")}</td><td>{dark_html}</td><td>{w.data_quality}</td><td>{missing_html}</td></tr>\n'

    # ledger panel placeholder
    ledger_placeholder = '<div id="ledger"></div>'
    completions_placeholder = '<div id="completions"></div>'
    prose_placeholder = '<div id="prose"></div>'
    coverage_placeholder = f'<div id="coverage">Coverage: {total} weeks, {with_pair} with pair, {with_bundle} with bundle, {with_both} with both, {total-with_both} missing</div>'
    failure_banner = '<div id="failure-banner" style="display:none;"></div>'

    # inline report HTML for the blog-style viewer (restricted renderer, escaped)
    reports_html = {}
    for w in sorted(weeks, key=lambda x: x.week_ending):
        entry = {}
        for key, p in (("dad", w.dad_report_path), ("personal", w.personal_report_path)):
            if p and Path(p).exists():
                try:
                    entry[key] = render_markdown_restricted(Path(p).read_text(encoding="utf-8", errors="replace"))
                except Exception:
                    entry[key] = ""
        if entry:
            reports_html[w.week_ending.isoformat()] = entry
    reports_json = json.dumps(reports_html, sort_keys=True, separators=(",", ":"))

    html_content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Weekly Report Dashboard</title>
<style>{css_text}</style>
</head>
<body>
<div class="dashboard-shell">
<header id="page-header">
<div style="display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;">
  <h1 style="margin:0;font-size:22px;">Weekly Report Dashboard</h1>
  <span style="font-size:12px;color:#8a8f98;">Generated {generated_at.strftime("%Y-%m-%d %H:%M UTC")} · refreshes Fri 8PM · {total} weeks · {with_pair} with reports · {with_bundle} with metric bundles</span>
  <a href="settings.html" style="margin-left:auto;font-size:12px;color:#8a8f98;">Settings</a>
</div>
<nav id="topnav">
  <a href="#attention">Attention</a>
  <a href="#this-week">This Week</a>
  <a href="#tasks">Tasks</a>
  <a href="#trends">Trends</a>
  <a href="#carry-over">Carry-Over</a>
  <a href="#data-sources">Data Sources</a>
  <a href="#appendix">Appendix</a>
</header>
{failure_banner}
<section id="attention">
<h2>Attention</h2>
<p class="section-sub">What needs action right now. Counts derive from the carry-over ledger, week records, and git state — nothing here is hand-entered. Items listed below the tiles are the specific things behind the numbers.</p>
<div class="attention-grid">
  <div class="attention-card severity-info" id="attention-stalled">
    <span class="card-icon">⏳</span>
    <span class="card-label">Stalled items</span>
    <span class="card-value">—</span>
    <span class="card-detail">computed from carry_over</span>
  </div>
  <div class="attention-card severity-info" id="attention-darkwork">
    <span class="card-icon">🌑</span>
    <span class="card-label">Dark work weeks</span>
    <span class="card-value">—</span>
    <span class="card-detail">computed</span>
  </div>
  <div class="attention-card severity-info" id="attention-coverage">
    <span class="card-icon">📊</span>
    <span class="card-label">Data coverage</span>
    <span class="card-value">{with_pair}/{total}</span>
    <span class="card-detail">{with_bundle} bundles</span>
  </div>
  <div class="attention-card severity-info" id="attention-neglected">
    <span class="card-icon">🕸️</span>
    <span class="card-label">Neglected projects</span>
    <span class="card-value">—</span>
    <span class="card-detail">computed from project_activity</span>
  </div>
  <div class="attention-card severity-info" id="attention-git">
    <span class="card-icon">🐙</span>
    <span class="card-label">Git health</span>
    <span class="card-value">—</span>
    <span class="card-detail">computed from git_stats</span>
  </div>
  <div class="attention-card severity-info" id="attention-freshness">
    <span class="card-icon">⚡</span>
    <span class="card-label">Data freshness</span>
    <span class="card-value">—</span>
    <span class="card-detail">computed from timestamps</span>
  </div>
</div>
</section>

<div class="action-items" id="action-items"></div>

<section id="this-week">
<h2>This Week</h2>
<p class="section-sub">The narrative behind the numbers: the latest weekly report, in full. The dashboard shows what happened; the report explains why it mattered. Pick any prior week to read its report.</p>
  <div id="weekly-summary" style="font-size:13px;color:#c2c7d0;line-height:1.5;padding:4px 0 10px;"></div>
  <div style="display:flex;gap:8px;align-items:center;margin:10px 0;">
    <button id="report-prev" class="btn">← prev</button>
    <select id="report-week" class="btn"></select>
    <button id="report-next" class="btn">next →</button>
  </div>
  <div id="report-viewer" style="column-count:2;column-gap:28px;font-size:13px;line-height:1.6;color:#d8dce2;"></div>
</section>

<section id="trends">
<h2>Trends</h2>
<p class="section-sub">Throughput over time from the canonical table. Lines connect every week that has data, jumping across gaps without inventing points — a missing week has no dot and shows "—" in the table. Figure 1 uses a log scale because session counts span three orders of magnitude.</p>
  <div id="figure1" class="chart chart-lazy" style="height:420px;"></div>
  <div id="figure2" class="chart chart-lazy" style="height:380px;"></div>
  <div id="figure1-table"></div>
  <div style="display:flex;gap:16px;">
    <div id="figure3" class="chart chart-lazy" style="height:360px;flex:1;"></div>
    <div id="figure4" class="chart chart-lazy" style="height:360px;flex:1;"></div>
  </div>
<section id="tasks">
<h2>Tasks</h2>
<p class="section-sub">Open work from two sources: your weekly reports (carry-over items) and every Living Documents project's tasks page, aggregated. Each item shows a one-line summary — expand it for the full detail, or click "Open in Living Documents" to go to the page where you complete it.</p>
<div id="tasks-source-tabs" class="ledger-tabs">
  <button class="ledger-tab active" data-src="ld">Living Documents</button>
  <button class="ledger-tab" data-src="reports">Weekly reports</button>
</div>
<input id="tasks-search" placeholder="Search tasks..." />
<div id="tasks-summary" style="font-size:12px;color:#8a8f98;margin:6px 0 10px;"></div>
<div id="tasks-list"></div>
</section>

<section id="carry-over">
<h2>Carry-Over Ledger</h2>
<p class="section-sub">Commitments carried unchecked from one week's report to the next, matched by text. Sorted by carry age — the oldest first. An item at or past the stall threshold needs an explicit complete-or-retire decision; that is the point of this list.</p>

  <input id="ledger-search" placeholder="Search items..." />
  {ledger_placeholder}
  {completions_placeholder}
</section>

<section id="data-sources">
<h2>Data Sources</h2>
<p class="section-sub">What the machine was doing, from primary logs — not from the reports. Each panel is one source. Model Telemetry answers which model/provider combination does the work, at what cost, and how often it fails. Open a panel to see its charts.</p>
<details class="data-panel" id="panel-telemetry">
  <summary><span class="panel-title">Model Telemetry</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-m1a" class="chart chart-lazy" style="height:400px;"></div>
    <div id="figure-m1b" class="chart chart-lazy" style="height:400px;"></div>
    <div id="group-m1-table"></div>
  </div>
</details>

<details class="data-panel" id="panel-projects">
  <summary><span class="panel-title">Projects</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-p1" class="chart chart-lazy" style="height:360px;"></div>
    <div id="figure-p2" class="chart chart-lazy" style="height:360px;"></div>
    <div id="group-p-table"></div>
  </div>
</details>

<details class="data-panel" id="panel-value">
  <summary><span class="panel-title">Value Extracted — subscriptions &amp; projects</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-v1" class="chart chart-lazy" style="height:340px;"></div>
    <div id="figure-v2" class="chart chart-lazy" style="height:400px;"></div>
    <div id="figure-v3" class="chart chart-lazy" style="height:300px;"></div>
    <div id="group-v-table"></div>
  </div>
</details>
<details class="data-panel" id="panel-git">
  <summary><span class="panel-title">Git Health</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-g1" class="chart chart-lazy" style="height:360px;"></div>
    <div id="figure-g2" class="chart chart-lazy" style="height:320px;"></div>
    <div id="group-g-table"></div>
  </div>
</details>

<details class="data-panel" id="panel-harness">
  <summary><span class="panel-title">Harness Activity</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-h1" class="chart chart-lazy" style="height:360px;"></div>
    <div id="figure-h2" class="chart chart-lazy" style="height:360px;"></div>
    <div id="group-h-table"></div>
  </div>
</details>

<details class="data-panel" id="panel-claude">
  <summary><span class="panel-title">Claude Code</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-cc1" class="chart chart-lazy" style="height:320px;"></div>
    <div id="figure-cc2" class="chart chart-lazy" style="height:320px;"></div>
    <div id="group-cc-table"></div>
  </div>
</details>

<details class="data-panel" id="panel-obsidian">
  <summary><span class="panel-title">Obsidian Vault</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-obs1" class="chart chart-lazy" style="height:320px;"></div>
    <div id="figure-obs2" class="chart chart-lazy" style="height:320px;"></div>
    <div id="group-obs-table"></div>
  </div>
</details>

<details class="data-panel" id="panel-browser">
  <summary><span class="panel-title">Browser</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-br1" class="chart chart-lazy" style="height:320px;"></div>
    <div id="figure-br2" class="chart chart-lazy" style="height:340px;"></div>
    <div id="group-br-table"></div>
  </div>
</details>

<details class="data-panel" id="panel-system">
  <summary><span class="panel-title">System</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-sys1" class="chart chart-lazy" style="height:320px;"></div>
    <div id="group-sys-table"></div>
  </div>
</details>

<details class="data-panel" id="panel-subvalue">
  <summary><span class="panel-title">Subscription Value</span><span class="panel-summary"></span></summary>
  <div class="panel-content">
    <div id="figure-sv1" class="chart chart-lazy" style="height:360px;"></div>
    <div id="figure-sv2" class="chart chart-lazy" style="height:360px;"></div>
    <div id="group-sv-table"></div>
  </div>
</details>
</section>

<section id="appendix">
<h2>Appendix</h2>
<p class="section-sub">Reference material: the full canonical table every chart derives from, the complete report archive, and the page's own validation state. Nothing here is needed for the weekly read — it is here so every number on the page can be traced.</p>
<details class="data-panel" id="panel-canonical">
  <summary><span class="panel-title">All Weeks (canonical table)</span><span class="panel-summary">One row per week — every chart above derives from this table. Click a row to read that week's report.</span></summary>
  <div class="panel-content">
  <p style="font-size:12px;color:#8a8f98;margin:0 0 10px;line-height:1.6;">
    <strong>How to read this:</strong>
    <span title="Sessions counted from raw harness logs (cass). Available for all 39 weeks."><u>Sessions</u></span> = work sessions logged that week ·
    <span title="Commits, files changed, active projects — only exist for weeks that have a metrics bundle (8 of 39)."><u>Commits/Files/Projects</u></span> = git activity, only where a bundle exists ·
    <span title="Sessions per commit. High = lots of work with little git activity (dark work)."><u>SPC</u></span> = sessions per commit ·
    <span title="● dark work = a week where session count is high relative to commits — work git can't see."><u>●</u></span> = dark-work week ·
    <span title="Coverage tells you which sources exist for that week: 'primary' = session logs only; 'pair' = a written report; 'bundle' = a metrics file. Most weeks are primary-only, which is why Commits shows —."><u>Coverage</u></span> = which sources exist ·
    <span title="'N missing' lists which fields had no data. Hover to see which."><u>Missing</u></span> = fields with no data (hover for the list).
  </p>
  <div id="canonical-table-wrap" style="max-height:420px;overflow-y:auto;border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:0 8px;">
  <input id="table-search" placeholder="Search weeks..." style="position:sticky;top:0;z-index:3;" />
  <table id="canonical-table">
  <thead><tr><th>Week</th><th>Coverage</th><th>Sessions</th><th>Commits</th><th>Files</th><th>Projects</th><th>Spc</th><th>Dark</th><th>Quality</th><th>Missing</th></tr></thead>
  <tbody>{table_rows}</tbody>
  </table>
  </div>
  </div>
</details>
<details class="data-panel" id="panel-reports-archive">
  <summary><span class="panel-title">Report Archive</span><span class="panel-summary">Every weekly report, searchable — read-only</span></summary>
  <div class="panel-content">
    <div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
      <input id="reports-search" placeholder="Search reports..." style="flex:1;min-width:200px;padding:8px;background:#08090a;color:#f7f8f8;border:1px solid #333;border-radius:6px;"/>
      <select id="reports-filter" style="padding:8px;background:#08090a;color:#f7f8f8;border:1px solid #333;border-radius:6px;">
        <option value="all">All reports</option>
        <option value="pair">With pair</option>
        <option value="primary">Primary-only</option>
      </select>
    </div>
    <div id="reports-list" style="max-height:420px;overflow:auto;border:1px solid rgba(255,255,255,0.06);border-radius:8px;"></div>
    <div id="reports-detail" style="margin-top:12px;padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;min-height:120px;"></div>
  </div>
</details>

<section id="diagnostics">
<h2>Page Health</h2>
<p class="section-sub">The dashboard validates its own invariants on every build. If a count looks wrong, check here first — a failed assertion means a data problem, not a rendering one.</p>
  <div class="diagnostics-grid">
    <div class="diag-card">
      <h3>Assertions</h3>
      <div id="assertions-summary"></div>
    </div>
    <div class="diag-card">
      <h3>Coverage Breakdown</h3>
      <div id="coverage-breakdown"></div>
    </div>
    <div class="diag-card">
      <h3>Data Quality</h3>
      <div id="data-quality-summary"></div>
    </div>
  </div>
</section>

</div>

<script>{vendor_js}</script>
<script>window.__WEEKLY__ = {payload_json};</script>
<script>window.__LLM_SUPPLEMENT__ = {llm_json};</script>
<script>window.__REPORTS_HTML__ = {reports_json};</script>
<script>{js_text}</script>
</body>
</html>
"""
    out_file = out_path / "index.html"
    out_file.write_text(html_content, encoding="utf-8")
    # also write settings.html
    try:
        from scripts.config import load_env
        env = load_env()
        cur = env.get("DASHBOARD_SCHEDULE") or env.get("DASHBOARD_CRON") or config.get("schedule","daily")
    except Exception:
        cur = config.get("schedule","daily")
    settings_html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>Dashboard Settings</title><style>{css_text}</style></head>
<body><header><h1>Dashboard Settings</h1><p style="color:#8a8f98;">Edit <code>config.env</code> — controls how often regeneration runs (cron). Changes take effect on next <code>schedule.py install</code> or next build.</p></header>
<div style="margin:24px;background:#14181b;border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:20px;">
<h2>Schedule</h2>
<p style="color:#8a8f98;font-size:13px;">Current: <code>{cur}</code> — from <code>config.env</code> (<code>DASHBOARD_SCHEDULE</code> / <code>DASHBOARD_CRON</code>)</p>
<label>Interval:</label>
<select id="schedule-select"><option value="hourly">hourly</option><option value="daily">daily</option><option value="weekly">weekly</option><option value="monthly">monthly</option><option value="custom">custom cron</option></select>
<input id="cron-input" placeholder='e.g. 0 9 * * *' style="margin-left:8px;padding:6px;background:#08090a;color:#f7f8f8;border:1px solid #333;border-radius:6px;width:160px;"/>
<button id="save-btn" style="margin-left:8px;padding:6px 12px;background:#7170ff;color:white;border:none;border-radius:6px;cursor:pointer;">Save to config.env</button>
<p id="save-status" style="color:#8a8f98;font-size:12px;margin-top:8px;"></p>
<pre id="env-preview" style="background:#08090a;padding:12px;border-radius:6px;overflow:auto;font-size:12px;">Loading…</pre>
<p style="font-size:12px;color:#8a8f98;">Save writes via <code>scripts/config.py</code> helper. If opened via <code>file://</code>, copy the preview below into <code>config.env</code> manually. When served (e.g. <code>python3 -m http.server</code>), Save will POST to <code>/__save_config</code> if a tiny helper server is running.</p>
<a href="index.html" style="color:#7170ff;">← Back to dashboard</a>
</div>
<script>
const curVal = "{cur}";
const sel = document.getElementById('schedule-select');
const cron = document.getElementById('cron-input');
const status = document.getElementById('save-status');
const preview = document.getElementById('env-preview');
function refreshPreview() {{
  const v = sel.value === 'custom' ? cron.value.trim() : sel.value;
  preview.textContent = `DASHBOARD_SCHEDULE=${{sel.value !== 'custom' ? sel.value : ''}}\nDASHBOARD_CRON=${{sel.value === 'custom' ? cron.value.trim() : ''}}\n# effective: ${{v}}`;
}}
if (['hourly','daily','weekly','monthly'].includes(curVal)) sel.value = curVal;
else if (curVal.includes('*')) {{ sel.value='custom'; cron.value=curVal; }}
else sel.value='daily';
refreshPreview();
sel.addEventListener('change', refreshPreview);
cron.addEventListener('input', refreshPreview);
document.getElementById('save-btn').addEventListener('click', async () => {{
  const body = sel.value === 'custom' ? {{DASHBOARD_CRON: cron.value.trim(), DASHBOARD_SCHEDULE: ''}} : {{DASHBOARD_SCHEDULE: sel.value, DASHBOARD_CRON: ''}};
  status.textContent = 'Saving…';
  try {{
    const r = await fetch('/__save_config', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify(body)}});
    if (r.ok) {{ status.textContent = 'Saved to config.env ✓'; }} else throw new Error(await r.text());
  }} catch(e) {{
    status.textContent = 'No server — copy preview into config.env manually. ('+e.message+')';
  }}
}});
</script>
</body></html>
"""
    (out_path / "settings.html").write_text(settings_html, encoding="utf-8")
    return out_file

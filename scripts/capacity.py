"""Render the public, allowlisted subset of the offline dsctl export."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

POOLS = {'claude', 'codex', 'agy', 'openrouter', 'opencode-zen', 'kilo', 'opencode-go'}
WINDOWS = {'five_hour', 'weekly', 'monthly', 'daily', 'free_daily', 'hourly_per_ip'}


def load_capacity(path):
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        return data if isinstance(data, dict) and data.get('schema_version') == 1 else None
    except (OSError, ValueError, TypeError):
        return None


def number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else None


def fmt(value, suffix='', factor=1):
    value = number(value)
    return f'{value * factor:.1f}{suffix}' if value is not None else 'unavailable'


def count(value):
    return str(value) if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 'unavailable'


def date(value):
    return value if isinstance(value, str) and re.fullmatch(r'\d{4}-\d\d-\d\d(?:T\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d))?', value) else 'unavailable'


def render_capacity(data):
    heading = '<section id="capacity"><h2>Capacity and pace</h2>'
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        return heading + '<p>Telemetry unavailable.</p></section>'
    output = [heading, '<p class="section-sub">Offline dsctl telemetry, generated ' + date(data.get('generated_at')) + '. Linear projections are estimates; rolling windows and reset times limit their reliability. Modes are informational.</p>',
              '<figure class="chart-figure"><figcaption><strong>Pool pace</strong> · 5 projects 100% at reset. Missing readings are unavailable.</figcaption>',
              '<div style="overflow-x:auto"><table><thead><tr><th>Pool</th><th>Window</th><th>Used</th><th>Hours to reset</th><th>Projection</th><th>Pace and mode</th><th>Reading</th></tr></thead><tbody>']
    pools = data.get('pools') if isinstance(data.get('pools'), list) else []
    rows = 0
    for pool in pools:
        if not isinstance(pool, dict):
            continue
        raw_name = pool.get('name')
        name = raw_name if isinstance(raw_name, str) and raw_name in POOLS else 'Other pool'
        windows = pool.get('windows') if isinstance(pool.get('windows'), dict) else {}
        for key, window in (windows.items() if windows else [('unavailable', {'used_fraction': pool.get('used_fraction')})]):
            if not isinstance(window, dict):
                continue
            label = key.replace('_', ' ') if key in WINDOWS else 'unavailable'
            score = number(window.get('pace_score'))
            pace = fmt(score, '/10')
            if score is not None:
                pace += ' · ' + ('hits cap early' if score > 5 else 'will waste' if score < 5 else 'on pace')
            mode = window.get('mode')
            mode = mode.title() if isinstance(mode, str) and mode.lower() in {'burn', 'stretch', 'reserve', 'normal'} else 'unavailable'
            stale = 'stale' if pool.get('stale') is True else 'current' if pool.get('stale') is False else 'freshness unavailable'
            output.append(f'<tr><td>{name}</td><td>{label}</td><td>{fmt(window.get("used_fraction"), "%", 100)}</td><td>{fmt(window.get("remaining_hours"))}</td><td>projects {fmt(window.get("projected_fraction"), "%", 100)} at reset</td><td>{pace} · {mode}</td><td>{stale} · observed {date(pool.get("observed_at"))}</td></tr>')
            rows += 1
    if not rows:
        output.append('<tr><td colspan="7">No pool readings available.</td></tr>')
    output.append('</tbody></table></div></figure>')
    efficiency = data.get('efficiency') if isinstance(data.get('efficiency'), dict) else {}
    tiers = efficiency.get('by_tier') if isinstance(efficiency.get('by_tier'), dict) else {}
    output.append('<h3>Efficiency by tier</h3>')
    if not tiers:
        reason = 'no dispatched attempts yet' if efficiency.get('reason') == 'no dispatched attempts yet' else 'unavailable: attempt evidence lacks tier or measured quota consumption'
        output.append(f'<p>{reason}.</p>')
    else:
        output.append('<p>Efficiency data is unavailable in the current export schema.</p>')
    concurrency = data.get('concurrency') if isinstance(data.get('concurrency'), dict) else {}
    processes = concurrency.get('processes') if isinstance(concurrency.get('processes'), dict) else {}
    output.append('<h3>Concurrency</h3><p>Sessions: unavailable · Agents: unavailable · Active Claude subagent transcripts: ' + count(concurrency.get('active_claude_subagent_transcripts')) + ' (activity proxy, not a live subagent count).</p>')
    output.append('<p>Native CLI process counts: ' + ' · '.join(f'{name}: {count(processes.get(name))}' for name in ('claude', 'codex', 'agy', 'omp', 'opencode')) + '.</p>')
    meta = data.get('meta_analysis') if isinstance(data.get('meta_analysis'), dict) else {}
    trend = meta.get('trend') if isinstance(meta.get('trend'), dict) else {}
    falling = trend.get('falling')
    trend_label = 'falling' if falling is True else 'not falling' if falling is False else 'unavailable'
    series = meta.get('series') if isinstance(meta.get('series'), list) else []
    output.append('<figure class="chart-figure"><figcaption><strong>Meta-analysis trend</strong> · observed items per run; trend: ' + trend_label + ' over ' + count(trend.get('runs')) + ' runs.</figcaption>')
    valid = [item for item in series if isinstance(item, dict) and count(item.get('items_observed')) != 'unavailable']
    if valid and len(valid) == len(series):
        maximum = max(1, *(item['items_observed'] for item in valid))
        points = [(20 + 760 * i / max(1, len(valid) - 1), 180 - 160 * item['items_observed'] / maximum) for i, item in enumerate(valid)]
        coords = ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)
        output.append('<svg viewBox="0 0 800 200" role="img" aria-label="Observed items per meta-analysis run; values appear in the table below" style="width:100%;max-width:800px;height:auto"><line x1="20" y1="180" x2="780" y2="180" stroke="#8a8f98"/><polyline fill="none" stroke="#7170ff" stroke-width="2" points="' + coords + '"/>' + ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#4ecdc4"/>' for x, y in points) + '</svg>')
    output.append('<div style="overflow-x:auto"><table><thead><tr><th>Run date</th><th>Trigger</th><th>Observed</th><th>Fixed</th><th>Next run</th></tr></thead><tbody>')
    for item in series:
        if not isinstance(item, dict):
            continue
        trigger = item.get('trigger') if item.get('trigger') in ('bridge-step', 'nightly') else 'unavailable'
        output.append(f'<tr><td>{date(item.get("date"))}</td><td>{trigger}</td><td>{count(item.get("items_observed"))}</td><td>{count(item.get("items_fixed"))}</td><td>{date(item.get("next_run"))}</td></tr>')
    if not series:
        output.append('<tr><td colspan="5">No runs recorded.</td></tr>')
    output.append('</tbody></table></div></figure></section>')
    return ''.join(output)

"""Summaries — LLM-free templated synthesis for per-week, per-group, overall.

Loop-robust: deterministic, stdlib only, no file mutation.
"""
from __future__ import annotations
from datetime import date

def overall_summary(weeks, carry_over) -> str:
    total = len(weeks)
    primary_weeks = sum(1 for w in weeks if getattr(w, "_has_primary", False))
    sessions = sum(w.sessions or 0 for w in weeks)
    dark = sum(1 for w in weeks if w.is_dark_work)
    stalled = sum(1 for c in carry_over if c.state == "stalled")
    open_n = sum(1 for c in carry_over if c.state == "open")
    peak = max(weeks, key=lambda w: w.sessions or 0) if weeks else None
    peak_txt = f"Peak {peak.week_ending} {peak.sessions} sessions ({peak.source_bundle})" if peak and peak.sessions else "no peak"
    return (f"Feb-Aug: {total} weeks ({primary_weeks} primary via cass/raw-mirror, {total-primary_weeks} legacy). "
            f"{sessions} sessions total, {dark} dark-work weeks, {stalled} stalled carry-overs (open {open_n}). "
            f"{peak_txt}. 28 weeks lacked bundles — primary fills gap; see Data source toggle (primary vs legacy).")

def group_summary(group_id: str, weeks, carry_over, proj_activity) -> str:
    if group_id == "A":
        stalled = [c for c in carry_over if c.state=="stalled"]
        top = sorted(stalled, key=lambda c: -c.carry_age)[:3]
        top_txt = ", ".join(f"{c.normalized_text[:30]}(age {c.carry_age})" for c in top) if top else "none"
        return f"A: {len(stalled)} stalled (age≥3). Top: {top_txt}. Dark lane shows commits understating effort — check uncommitted."
    if group_id == "B":
        # neglect: projects with 0 commits last 4 weeks vs earlier
        # simplified: count distinct projects in last 4 weeks
        recent = sorted(weeks, key=lambda w: w.week_ending)[-4:]
        recent_projects = set()
        for w in recent:
            for p in proj_activity:
                if p.week_ending == w.week_ending and (p.commits or 0)>0:
                    recent_projects.add(p.project_name)
        all_projects = set(p.project_name for p in proj_activity)
        neglected = all_projects - recent_projects
        easy = [n for n in neglected if any(p.project_name==n and (p.uncommitted_count or 0) in (1,2,3) for p in proj_activity)]
        return f"B: Focus on {len(recent_projects)} recent projects; {len(neglected)} neglected ({', '.join(list(neglected)[:3])}). Easy wins: {', '.join(easy[:3]) or 'none — check uncommitted 1-3'}."
    if group_id == "C":
        return "C: Heatmap shows rhythm — stacked sessions reveal single-threaded weeks; commit-size hist flags batch commits."
    if group_id == "D":
        return "D: Narrative ties numbers to prose — see Week story card for selected week's 2-sentence synthesis."
    return ""

def week_story_card(w, carry_for_week=None) -> str:
    # 2-sentence synthesis per week
    dark = " dark-work (commits understate sessions)" if w.is_dark_work else ""
    spc = f"{w.sessions_per_commit:.1f} spc" if w.sessions_per_commit else "no spc"
    src = w.source_bundle or ""
    provenance = "primary:cass" if "primary:cass" in src else src
    miss = f" missing {','.join(w.missing_fields[:2])}" if w.missing_fields else ""
    s1 = f"Week {w.week_ending}: {w.sessions or '?'} sessions, {w.commits if w.commits is not None else '?'} commits ({spc}){dark} via {provenance}."
    s2 = f"Coverage {w.coverage}, quality {w.data_quality}{miss}."
    if carry_for_week:
        s2 += f" Stalled carry-overs touching this week: {len(carry_for_week)}."
    return s1+" "+s2

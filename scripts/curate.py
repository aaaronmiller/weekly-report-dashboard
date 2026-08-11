"""Report curation — classify passages, preserve job-search/meetup, never delete."""
from __future__ import annotations

import re
from pathlib import Path

# Rules that fire: each returns label (legacy simple)
RULES = [
    ("process_meta", re.compile(r"(carry-over|process|workflow|pipeline|retrospective)", re.I)),
    ("job_search", re.compile(r"(job|application|interview|career|meetup)", re.I)),
]

# Weighted improved rules: (label, pattern, weight)
WEIGHTED_RULES = [
    ("process", re.compile(r"carry-over", re.I), 3),
    ("process", re.compile(r"process meta|workflow|pipeline discussion|retrospective|sprint|standup|ceremony", re.I), 2),
    ("process", re.compile(r"\b(process|workflow|pipeline)\b.*\b(discussion|meeting|review|planning)\b", re.I), 2),
    ("keep", re.compile(r"job|application|interview|career|meetup|hiring|offer", re.I), 10),  # protection: dominates
    ("keep", re.compile(r"feature|deliverable|ship|implement|build|fix|bug|release", re.I), 1),
]

def classify_passages(text: str, algorithm: str = "weighted") -> list[dict]:
    """Dispatch: default (better) weighted, alternative legacy rule-based."""
    if algorithm == "legacy" or algorithm == "rule_based":
        return _classify_legacy(text)
    return _classify_weighted(text)


def _classify_legacy(text: str) -> list[dict]:
    """Legacy rule-based (alternative): simple regex, job-search always keep."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    result = []
    for para in paragraphs:
        label = "keep"
        rule = "none"
        if re.search(r"(job|application|career|meetup|interview)", para, re.I):
            label = "keep"
            rule = "job_search_retention"
        elif re.search(r"(carry-over|process meta|workflow|pipeline discussion|retrospective)", para, re.I):
            label = "process"
            rule = "process_meta"
        result.append({"passage": para, "label": label, "rule": rule})
    return result


def _classify_weighted(text: str) -> list[dict]:
    """Improved weighted classifier (default, better): scores per passage, job-search hard protection."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    result = []
    for para in paragraphs:
        # Hard protection: job-search/meetup never eligible for process — retention always wins
        if re.search(r"(job|application|career|meetup|interview|hiring)", para, re.I):
            result.append({"passage": para, "label": "keep", "rule": "job_search_retention"})
            continue
        # score process signals vs keep signals
        process_score = 0
        keep_score = 0
        triggered_rule = "none"
        max_weight = 0
        for label, pat, weight in WEIGHTED_RULES:
            if pat.search(para):
                if label == "process":
                    process_score += weight
                    if weight > max_weight:
                        max_weight = weight
                        triggered_rule = f"process_weighted:{pat.pattern[:30]}"
                else:
                    # keep signals besides the hard-protected one
                    if label == "keep" and weight < 10:
                        keep_score += weight
        # Also length-normalize: very short paragraphs (<30 chars) less likely process meta
        if len(para) < 30:
            process_score = max(0, process_score - 1)
        # Double carry-over bonus
        if len(re.findall(r"carry-over", para, re.I)) >= 2:
            process_score += 2
        if process_score > keep_score and process_score >= 2:
            result.append({"passage": para, "label": "process", "rule": triggered_rule or "process_weighted"})
        else:
            result.append({"passage": para, "label": "keep", "rule": "keep_weighted"})
    return result

# Backwards compat: legacy name
def classify_passages_legacy(text: str) -> list[dict]:
    return _classify_legacy(text)

def classify_passages_weighted(text: str) -> list[dict]:
    return _classify_weighted(text)

def job_search_protected(text: str) -> bool:
    return bool(re.search(r"(job|career|meetup)", text, re.I))

def curate_file(path: Path) -> dict:
    """Surface classification summary; source Markdown is byte-identical before and after."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    original = text
    classified = classify_passages(text)
    # verify no modification
    assert Path(path).read_text(encoding="utf-8", errors="replace") == original, "source modified"
    summary = {
        "total": len(classified),
        "by_rule": {},
        "by_label": {},
    }
    for c in classified:
        summary["by_rule"][c["rule"]] = summary["by_rule"].get(c["rule"], 0) + 1
        summary["by_label"][c["label"]] = summary["by_label"].get(c["label"], 0) + 1
    return {"classified": classified, "summary": summary}

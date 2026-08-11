"""Data models for Weekly Report Dashboard — dataclasses per data-model.md."""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class WeekRecord:
    week_ending: date
    period_start: date | None = None
    period_end: date | None = None
    has_pair: bool = False
    has_bundle: bool = False
    coverage: str = "pair-only"  # pair+bundle | pair-only | bundle-only
    sessions: int | None = None
    commits: int | None = None
    files_changed: int | None = None
    projects_active: int | None = None
    sessions_per_commit: float | None = None
    uncommitted_changes: int | None = None
    momentum_score: int | None = None
    dad_report_path: str | None = None
    personal_report_path: str | None = None
    dad_word_count: int | None = None
    agent_breakdown: dict[str, int] | None = None
    daily_sessions: list[dict] | None = None
    is_dark_work: bool = False
    data_quality: str = "unavailable"  # verified | estimated | unavailable
    missing_fields: list[str] = field(default_factory=list)
    source_bundle: str | None = None
    retrieved_at: datetime | None = None


@dataclass
class CarryOverItem:
    item_text: str
    normalized_text: str
    project_heading: str
    first_seen_week: date
    last_seen_week: date
    carry_age: int
    state: str  # open | stalled | completed
    completed_week: date | None = None
    weeks_carried_before_completion: int | None = None
    match_confidence: str = "exact"  # exact | normalized | uncertain
    appearances: list[dict] = field(default_factory=list)


@dataclass
class ProjectWeekActivity:
    week_ending: date
    project_name: str
    commits: int | None = None
    files_changed: int | None = None
    uncommitted_count: int | None = None
    state: str | None = None


@dataclass
class ValidationAssertion:
    assertion_id: str
    description: str
    expected: object = None
    actual: object = None
    passed: bool = False

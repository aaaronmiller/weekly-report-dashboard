# Data Model: Weekly Report Dashboard

All entities are Python dataclasses in `scripts/models.py`, serialized into one
embedded JSON literal. There is no database.

The governing rule is Constitution Principle II: a field that was not observed is
`None`, never `0`. Every entity therefore carries an explicit record of what is
missing rather than relying on falsy values.

## WeekRecord

One row per week-ending date. Primary key: `week_ending`.

| Field | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `week_ending` | `date` | no | Primary key, ISO format |
| `period_start` | `date` | yes | From bundle; null when bundle absent |
| `period_end` | `date` | yes | From bundle |
| `has_pair` | `bool` | no | Report pair discovered |
| `has_bundle` | `bool` | no | Metrics bundle discovered |
| `coverage` | `enum` | no | `pair+bundle` \| `pair-only` \| `bundle-only` |
| `sessions` | `int` | yes | Null when no bundle |
| `commits` | `int` | yes | |
| `files_changed` | `int` | yes | |
| `projects_active` | `int` | yes | |
| `sessions_per_commit` | `float` | yes | Null when commits is null **or zero** |
| `uncommitted_changes` | `int` | yes | Null for weeks predating collection |
| `momentum_score` | `int` | yes | |
| `dad_report_path` | `str` | yes | |
| `personal_report_path` | `str` | yes | |
| `dad_word_count` | `int` | yes | |
| `agent_breakdown` | `dict[str,int]` | yes | agent name to session count |
| `daily_sessions` | `list[dict]` | yes | `{date, sessions}` |
| `is_dark_work` | `bool` | no | `sessions_per_commit` above threshold |
| `data_quality` | `enum` | no | `verified` \| `estimated` \| `unavailable` |
| `missing_fields` | `list[str]` | no | Empty list, never null |
| `source_bundle` | `str` | yes | Provenance: originating file |
| `retrieved_at` | `datetime` | yes | Provenance: collection time |

### Invariants

- `sessions_per_commit` is null exactly when `commits` is null or zero. Division
  by zero must not produce infinity, and zero commits with nonzero sessions is
  the dark-work case the flag handles separately.
- `uncommitted_changes` is null, never zero, for any week before uncommitted
  collection began. Zero would falsely assert an observation.
- `missing_fields` is always a list. An empty list means nothing is missing; a
  null would be ambiguous.
- `coverage` is derived, never stored independently of `has_pair`/`has_bundle`.

## CarryOverItem

A commitment tracked across weeks. Primary key:
`(normalized_text, project_heading)`.

| Field | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `item_text` | `str` | no | As written in the most recent appearance |
| `normalized_text` | `str` | no | Matching key |
| `project_heading` | `str` | no | Owning project from the personal report |
| `first_seen_week` | `date` | no | |
| `last_seen_week` | `date` | no | |
| `carry_age` | `int` | no | Consecutive unchecked appearances |
| `state` | `enum` | no | `open` \| `stalled` \| `completed` |
| `completed_week` | `date` | yes | Null while open |
| `weeks_carried_before_completion` | `int` | yes | Null while open |
| `match_confidence` | `enum` | no | `exact` \| `normalized` \| `uncertain` |
| `appearances` | `list[dict]` | no | `{week, checked}` full history |

### Normalization rule

```
lowercase
strip trailing parenthetical  e.g. "(carry-over from Jul 11, Jul 19)"
collapse internal whitespace
strip leading/trailing punctuation
```

`- [ ] Week-over-week trend comparison (carry-over from Jul 11, Jul 19, Jul 25)`
normalizes to `week-over-week trend comparison`, matching the same item in the
week where it appeared without annotation.

### Invariants

- `carry_age` counts **consecutive** unchecked appearances. An item that is
  unchecked, checked, then unchecked again restarts at 1, since the commitment
  was met and later reopened.
- `state` is `stalled` when `carry_age >= stall_threshold` (default 3).
- `match_confidence` of `uncertain` means the item was **not** merged with a
  similar one. Uncertain items appear separately.
- `weeks_carried_before_completion` is set only on transition to `completed`.

## ProjectWeekActivity

Per project per week. Primary key: `(week_ending, project_name)`.

| Field | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `week_ending` | `date` | no | FK to WeekRecord |
| `project_name` | `str` | no | |
| `commits` | `int` | yes | |
| `files_changed` | `int` | yes | |
| `uncommitted_count` | `int` | yes | Null for historic weeks |
| `state` | `str` | yes | From bundle, e.g. `active` |

## ValidationAssertion

Emitted into the page as data so the browser can render its own health.

| Field | Type | Notes |
| --- | --- | --- |
| `assertion_id` | `str` | e.g. `A-004` |
| `description` | `str` | Human-readable statement |
| `expected` | `any` | |
| `actual` | `any` | |
| `passed` | `bool` | |

### Assertion set

| ID | Statement |
| --- | --- |
| A-001 | Every week has a report pair or a bundle |
| A-002 | Week-ending dates are unique |
| A-003 | `sessions_per_commit` is null exactly when commits is null or zero |
| A-004 | No `uncommitted_changes` is zero for a week predating collection |
| A-005 | Carry ages are monotonic per item across consecutive weeks |
| A-006 | Week count equals discovered reports minus duplicates |
| A-007 | No figure references a week absent from the canonical table |

## Access Patterns

All served from the single embedded table; no index structures required at the
corpus sizes involved.

| Pattern | Consumer | Operation |
| --- | --- | --- |
| All weeks by date ascending | Figures 1, 2 | sort by `week_ending` |
| One week by key | Figures 3, 4, prose panel | lookup by `week_ending` |
| Open items by carry age descending | Carry-over ledger | filter `state != completed`, sort desc |
| Weeks where `is_dark_work` | Dark-work annotations | filter |
| Weeks where `missing_fields` non-empty | Coverage panel | filter |
| Project activity for a week | Figure 4 | filter by `week_ending` |

## Lifecycle

The corpus is append-only in practice: a new report pair and bundle appear each
week. Records are never updated in place; the entire canonical table is rebuilt
from source on every run.

Consequently there is no migration strategy and no schema versioning beyond
`schema_version` in the embedded payload. Schema drift among historic bundles is
absorbed at ingest per FR-014, never by rewriting the historic files, which are
evidence.

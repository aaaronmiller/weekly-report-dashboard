# Weekly Report Dashboard -- Technical Design v1.0

## 1. Architecture Overview

A build-time generator and a zero-dependency runtime artifact.

```
  /code/weekly-reports/*.md ──┐
                              ├──→ ingest ──→ canonical ──→ validate ──→ emit
  /code/weekly-report-        │              WeekRecord[]       │          │
    dashboard/*/weekly-       │              CarryOverItem[]    │          │
    metrics.json ─────────────┘              ProjectWeek[]      │          ▼
                                                                │    index.html
  git status (live) ────────────────────────────────────────────┘   (self-contained)
```

Four stages, each independently testable:

1. **Ingest** -- read reports, bundles, and live git state into raw records.
2. **Canonicalize** -- reconcile by week-ending date into one table.
3. **Validate** -- assert invariants; collect results as data, not exceptions.
4. **Emit** -- serialize the canonical table into a single HTML file with the
   chart library and all CSS/JS inlined.

The canonical table is computed **once**, in Python, and embedded as a single
JSON literal. The browser never recomputes it. This is the structural expression
of FR-001: there is exactly one dataset, and every figure indexes into it.

### 1.1 What This System Does NOT Do

- Does not write, edit, or move any weekly report.
- Does not serve HTTP or require a running process.
- Does not fetch anything at runtime.
- Does not own tasks; Living Documents remains task authority.
- Does not forecast; it reports observed history only.
- Does not replace Prometheus/Grafana for live operational metrics.

## 2. Technology Stack

| Layer | Choice | Version |
| --- | --- | --- |
| Generator | Python | 3.11+ (stdlib only) |
| Charts | Apache ECharts | 5.x, vendored |
| Markdown | Custom minimal renderer | stdlib `re` |
| Tests | pytest | existing suite convention |
| Output | Single `index.html` | no runtime deps |

### 2.1 Technology Decision Records

**TDR-001: Apache ECharts over Chart.js, Plotly, or D3.**

Two requirements decide this, and only ECharts satisfies both natively:

- FR-041 (hover focuses a series and dims the others) maps to ECharts
  `emphasis: { focus: 'series', blurScope: 'coordinateSystem' }`. This is the
  `emphasis`/`blur`/`select` state model introduced in ECharts 5.0. Chart.js has
  no series-blur concept; implementing it means manual color mutation on every
  hover event.
- FR-042 (labels must never overlap) maps to
  `labelLayout: { hideOverlap: true }`, a built-in collision resolver. Chart.js
  requires a third-party plugin; D3 requires hand-written collision detection.

ECharts also provides log axes, `connectNulls: false` for the explicit gaps
required by FR-046, and canvas rendering that stays responsive at the point
counts involved. Plotly's bundle is substantially larger against the 3 MB budget
in NFR-003. D3 offers unlimited flexibility at the cost of writing axes,
legends, and tooltips by hand, which is unjustified for fixed chart types.

The 2026-07-03 complaint that graphs were "hard as fuck to read" with
overlapping labels and no visible population is a direct argument for a library
whose collision handling and focus behavior are native rather than bolted on.

**TDR-002: Vendor the library; do not use a CDN.**

NFR-020 forbids runtime network access and FR-063/AS-7 require offline
operation. The minified ECharts build is committed under `vendor/` and inlined
into the output at emit time. This pins the version, makes builds reproducible
per NFR-031, and removes a supply-chain path. Cost: roughly 1 MB of the 3 MB
budget, which is the dominant page-weight line item and is accepted knowingly.

**TDR-003: Python stdlib only for the generator.**

The generator reads Markdown and JSON and writes HTML. `re`, `json`, `pathlib`,
`datetime`, and `subprocess` cover it. Adding a dependency would need
justification under the standing rule that a dependency requires a recorded
reason why existing options are inadequate. There is none here.

**TDR-004: Static HTML rather than Grafana.**

Grafana and Prometheus are already provisioned in the suite, and the user
confirmed that pairing on 2026-05-19. They remain correct for live operational
metrics. They are wrong for this artifact: Grafana requires a running server and
a live datasource, while this must open from disk, work offline, and remain
readable years later as a historical record. The two are complementary, not
competing. Prometheus keeps live metrics; this owns narrative history.

**TDR-005: Custom minimal Markdown renderer.**

The reports use headings, paragraphs, tables, checkboxes, bold, and code spans.
A full CommonMark implementation is more surface than needed and adds a
dependency. A restricted renderer handling exactly that subset, escaping
everything first per NFR-021, is roughly 80 lines and safer by construction.

## 3. Data Model

### 3.1 Schema Design

**WeekRecord** -- primary key `week_ending` (ISO date).

| Field | Type | Null | Notes |
| --- | --- | --- | --- |
| `week_ending` | date | no | PK |
| `period_start` / `period_end` | date | yes | from bundle |
| `has_pair` / `has_bundle` | bool | no | coverage classification |
| `sessions` | int | yes | null when no bundle |
| `commits` | int | yes | |
| `files_changed` | int | yes | |
| `projects_active` | int | yes | |
| `sessions_per_commit` | float | yes | null when commits is 0 or null |
| `uncommitted_changes` | int | yes | null for historic weeks; **never 0** |
| `momentum_score` | int | yes | |
| `dad_report_path` / `personal_report_path` | str | yes | |
| `dad_word_count` | int | yes | |
| `agent_breakdown` | dict | yes | agent -> sessions |
| `daily_sessions` | list | yes | date -> count |
| `data_quality` | enum | no | verified / estimated / unavailable |
| `missing_fields` | list | no | explicit, drives the coverage panel |
| `source_bundle` | str | yes | provenance |
| `retrieved_at` | datetime | yes | provenance |

`uncommitted_changes` is null rather than zero for weeks predating collection.
This is FR-003 in the schema: a zero would assert "we looked and found nothing
uncommitted", which is false for historic weeks.

**CarryOverItem** -- primary key `(normalized_text, project_heading)`.

| Field | Type | Notes |
| --- | --- | --- |
| `item_text` | str | as written, for display |
| `normalized_text` | str | lowercased, punctuation and parentheticals stripped |
| `project_heading` | str | owning project |
| `first_seen_week` / `last_seen_week` | date | |
| `carry_age` | int | consecutive unchecked appearances |
| `state` | enum | open / stalled / completed |
| `completed_week` | date | null while open |
| `weeks_carried_before_completion` | int | null while open |
| `match_confidence` | enum | exact / normalized / uncertain |

**ValidationAssertion** -- `assertion_id`, `description`, `expected`, `actual`,
`passed`. Emitted into the page so the browser can render its own failure banner
per FR-006.

### 3.2 Relationships and Access Patterns

One `WeekRecord` per week; many `ProjectWeekActivity` per week; `CarryOverItem`
spans weeks and is the only cross-week entity.

Access patterns, all served by the single embedded table:

1. All weeks ordered by date -> trend figures.
2. One week by key -> detail panel and prose.
3. Open items sorted by carry age descending -> carry-over ledger.
4. Weeks where `sessions_per_commit > threshold` -> dark-work flags.
5. Weeks where `missing_fields` is non-empty -> coverage panel.

### 3.3 Migration Strategy

No migration. The corpus is read-only input and the output is regenerated whole.
Schema drift across the six existing bundles is absorbed at ingest by field-level
tolerance (FR-014) rather than by normalizing the historic files, which would
mutate evidence.

## 4. Component Specifications

### 4.1 `scripts/ingest.py`

Reads the corpus. Pure functions, no writes.

- `discover_reports(dir) -> dict[date, ReportPair]`
- `discover_bundles(dir) -> dict[date, dict]`
- `parse_carry_over(personal_md) -> list[RawCheckboxItem]`
- `collect_git_state(project_dirs) -> dict[str, int]` -- `git status --porcelain`
  counts per project, the mechanism closing the FR-021 gap that made the
  2026-08-01 week unmeasurable.

Every reader returns `(value, problems)`. A malformed bundle yields `None` plus
a problem record; it never raises. This is NFR-010.

### 4.2 `scripts/canonicalize.py`

- `build_week_records(reports, bundles, git) -> list[WeekRecord]`
- `build_carry_over_ledger(reports) -> list[CarryOverItem]`
- `normalize_item(text) -> str` -- lowercase, strip punctuation, collapse
  whitespace, remove trailing parentheticals such as
  `(carry-over from Jul 11, Jul 19)` so the same item matches across weeks while
  its annotation varies.
- `compute_carry_age(items) -> None` -- consecutive-week walk.

Matching is deliberately conservative per FR-034. Exact match wins; normalized
match is accepted and labeled; anything below stays a separate item marked
`uncertain`. A false merge silently understates carry age, which is the metric
the project exists to produce, so the failure mode is chosen to be visible.

### 4.3 `scripts/validate.py`

Returns assertions as data:

- `A-001` every week has a report pair or a bundle
- `A-002` week-ending dates are unique
- `A-003` `sessions_per_commit` is null exactly when commits is null or zero
- `A-004` no `uncommitted_changes` is zero for a week predating collection
- `A-005` carry ages are monotonic per item across consecutive weeks
- `A-006` week count equals reports discovered minus duplicates
- `A-007` no figure references a week absent from the canonical table

### 4.4 `scripts/emit.py`

- `render(canonical, assertions, out_dir) -> Path`
- Inlines vendored ECharts, CSS, and the canonical JSON.
- Escapes all report text before injection (NFR-021).
- Scrubs `/home/<user>` to `~` (NFR-022).
- Writes with sorted keys and fixed separators so byte-identical output follows
  from unchanged input (FR-061, SC-5).

### 4.5 `scripts/build_dashboard.py`

Entry point. Runs the four stages, prints a summary of what was ingested and
what was skipped with reasons (FR-063), and exits non-zero on any failed
assertion (FR-062).

## 5. API / Interface Contracts

### 5.1 CLI

```bash
python3 scripts/build_dashboard.py \
  --reports  /home/cheta/code/weekly-reports \
  --bundles  /home/cheta/code/weekly-report-dashboard \
  --out      /home/cheta/code/weekly-report-dashboard \
  [--weeks N] [--dark-work-threshold 8.0] [--stall-age 3] [--check]
```

`--check` validates and reports without writing. Exit codes: `0` success,
`1` assertion failed, `2` no input discovered.

### 5.2 Embedded data contract

```js
window.__WEEKLY__ = {
  schema_version: 1,
  generated_at: "ISO-8601",
  weeks: [ /* WeekRecord */ ],
  carry_over: [ /* CarryOverItem */ ],
  project_activity: [ /* ProjectWeekActivity */ ],
  assertions: [ /* ValidationAssertion */ ],
  coverage: { weeks_total, with_pair, with_bundle, with_both, missing }
}
```

Read-only to the page. No mutation after load; every view is a projection.

## 6. UX Architecture

### 6.1 Interaction Model

Single scrolling page, ordered so evidence precedes interpretation:

1. **Header** -- current week, coverage counts, validation banner if failing.
2. **Canonical table** -- searchable, sortable, all weeks. First, per FR-002.
3. **Figure 1: Throughput trend** -- sessions, commits, files changed over all
   weeks. Explicit gaps for missing weeks.
4. **Figure 2: Dark work** -- sessions-per-commit with threshold band; flagged
   weeks annotated.
5. **Figure 3: Intra-week distribution** -- daily sessions for the selected week.
6. **Figure 4: Project activity** -- per project per week, commits and
   uncommitted counts.
7. **Carry-over ledger** -- open items by descending age; stalled marked;
   completions with weeks-carried.
8. **Report prose** -- dad and personal reports for the selected week.
9. **Coverage and provenance panel** -- what is missing and why.

Week selection is a single control affecting figures 3, 4, and the prose.

### 6.2 Design System Alignment

Dark mode primary (NFR-040). Neutral dark ground, one accent for the current
week, muted palette for historic series. Series carry both color and marker
shape (NFR-042). Every figure is followed by its data table (NFR-043).

Chart interaction:

```js
emphasis:   { focus: 'series', blurScope: 'coordinateSystem' },
labelLayout:{ hideOverlap: true },
series:     { connectNulls: false }
```

Those three settings implement FR-041, FR-042, and FR-046 respectively.

### 6.3 Adoption and Onboarding

No onboarding. One command produces one file that opens in a browser. The
existing `render_dashboard.py` remains until this reaches parity, then is
retired with a note in the suite skill.

## 7. Hosting and Deployment

### 7.1 Infrastructure

None. The artifact is a local file. This is a deliberate consequence of NFR-020
and the requirement that it remain readable as a historical record without any
running service.

### 7.2 CI/CD Pipeline

Invoked by the weekly-report-suite skill after report generation. `--check` is
suitable as a pre-commit gate since it exits non-zero on failed invariants.

### 7.3 Environment Strategy

Single environment. No configuration beyond CLI flags.

## 8. Security Considerations

### 8.1 Threat Model

The artifact contains operational detail: project names, paths, session counts,
and career notes. The realistic threat is accidental publication, not remote
attack. There is no server, no input surface, and no network path.

### 8.2 Authentication / Authorization

None. Filesystem permissions are the control.

### 8.3 Data Protection

Home paths scrubbed to `~`. No credentials, tokens, or provider keys are read or
emitted. Report text is HTML-escaped before injection, which also prevents a
report containing Markdown-embedded HTML from executing in the page.

### 8.4 Supply Chain Security

One vendored dependency, version-pinned, integrity-checked at build time, never
fetched at runtime. This is a smaller surface than a CDN reference and the
reason TDR-002 accepts the page-weight cost.

## 9. Implementation Phases

### Phase 1: Data layer
Ingestion, canonicalization, validation, tests against the real 13-week corpus.
Exit criterion: canonical table correct, all assertions pass, no writes.

### Phase 2: Static emission
Emit with the canonical table and coverage panel; no charts yet. Exit criterion:
offline-openable, byte-identical on repeat runs.

### Phase 3: Figures
Vendor ECharts; implement figures 1-4 with focus, label collision, and explicit
gaps. Exit criterion: AS-1 through AS-4 demonstrable.

### Phase 4: Carry-over ledger and prose
Ledger with ages and completions; report rendering; week selector. Exit
criterion: AS-3 shows the trend-comparison item at age 4.

### Phase 5: Integration
Wire into the suite skill; document; retire the single-week renderer. Exit
criterion: one command regenerates from a clean checkout.

## 10. Testing Strategy

### 10.1 Unit Tests
- Carry-over normalization: parenthetical stripping, case, punctuation
- Carry age across consecutive and non-consecutive weeks
- `sessions_per_commit` null handling when commits is zero
- Bundle schema drift: absent fields yield null, never an exception
- Path scrubbing and HTML escaping
- Checkbox parsing including nested and malformed lines

### 10.2 Integration Tests
- Full build against the real corpus; assert 13 weeks discovered
- Malformed bundle injected: run completes, week is skipped and reported
- Idempotence: two runs, identical bytes
- `--check` exits non-zero when an invariant is broken
- Known-week fixture: 2026-08-01 flagged dark-work with 122 sessions, 23 commits
- The four-week-old trend-comparison item reports carry age 4

### 10.3 Manual Verification
Open the file with networking disabled and confirm every figure, tooltip,
legend toggle, and selector functions. Per the standing rule, visual correctness
requires looking at the rendered page; DOM presence is not visual verification.

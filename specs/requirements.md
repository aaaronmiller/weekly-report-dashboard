# Weekly Report Dashboard -- Requirements Specification v1.0

## 1. Purpose

Turn the weekly report corpus and its evidence bundle into a navigable operating
history that shows trend, not just a single week's totals.

Thirteen weekly report pairs exist (2026-05-23 through 2026-08-01) plus six
metrics bundles. Each bundle is rendered into an isolated single-week page. There
is no view across weeks, so the two questions the corpus exists to answer cannot
currently be answered:

1. Is throughput rising or falling, and against what baseline?
2. Which committed intentions were carried rather than completed, and for how
   many consecutive weeks?

"Week-over-week trend comparison" has been an explicit carry-over item in the
personal report for four consecutive weeks (2026-07-11, 07-19, 07-25, 08-01). It
is the single most-deferred item in the corpus. That is the problem this project
closes.

A second, sharper problem was proven in the 2026-08-01 report. The collector
recorded 23 commits for the week while the week's largest deliverable -- nine
gateway modules with 174 passing tests -- was entirely untracked and therefore
invisible to every metric. All 23 commits landed 2026-07-28/29; 110 of 122
sessions fell on 2026-07-30..08-01 and produced no commits at all. **A dashboard
that charts commits alone systematically misrepresents weeks like that one.**

## 2. Glossary

| Term | Meaning |
| --- | --- |
| **Report pair** | One dad-facing report plus one personal report for the same week-ending date |
| **Bundle** | A dated directory holding `weekly-metrics.json` plus rendered artifacts |
| **Canonical table** | The single derived dataset from which every figure, count, and label is computed |
| **Carry-over** | An unchecked `[ ]` item repeated from a prior week's personal report |
| **Carry age** | Number of consecutive weeks a carry-over item has appeared unchecked |
| **Dark work** | Sessions producing no commits; uncommitted or exploratory effort |
| **Provenance** | The source, retrieval time, and confidence attached to a value |
| **Coverage gap** | A week with a report pair but no metrics bundle, or the reverse |

## 3. User Scenarios

### 3.1 Primary User Story

As the operator of a large multi-agent workspace, I want to open one page and see
how this week compares to the last twelve, which commitments I keep deferring,
and where the numbers are untrustworthy, so that I can direct next week's effort
from evidence instead of from the most recent week's impression.

### 3.2 Acceptance Scenarios

**AS-1 Trend is visible.** Given 13 report pairs, when the dashboard opens, then
sessions, commits, files changed, and active projects render as a time series
across all weeks with the current week marked, and each point states its
week-ending date.

**AS-2 Dark work is exposed.** Given a week with 122 sessions and 23 commits,
when that week is displayed, then sessions-per-commit is shown as a distinct
series and any week exceeding the dark-work threshold is visually flagged.

**AS-3 Carry-over is aged.** Given `[ ] Week-over-week trend comparison` appears
unchecked in four consecutive personal reports, when the carry-over panel
renders, then the item shows carry age 4 and sorts above younger items.

**AS-4 Missing weeks are visible, not skipped.** Given bundles exist for only 6
of 13 weeks, when the trend renders, then weeks lacking a bundle appear as
explicit gaps with a stated reason, never as interpolated or omitted points.

**AS-5 Provenance is inspectable.** Given a metric derived from a fallback
source, when the user hovers it, then the tooltip states the source, retrieval
time, and whether the value is verified, estimated, or unavailable.

**AS-6 The page validates itself.** Given the canonical table is assembled, when
the page loads, then it asserts its own row counts and displays a failed
validation banner if any assertion does not hold.

**AS-7 It works offline.** Given no network, when `index.html` is opened from
disk, then every chart, table, and interaction functions.

## 4. Functional Requirements

### 4.1 Canonical Data Layer

- **FR-001** The system MUST build one canonical table of week records before
  rendering any figure. Every chart, count, label, tooltip, and conclusion MUST
  derive from that table. No separate hand-maintained list may exist.
- **FR-002** The canonical table MUST be printed as a visible, searchable,
  sortable table in the page before the analytical figures.
- **FR-003** Missing values MUST remain `null` and MUST NOT be coerced to zero.
  A zero MUST mean an observed zero.
- **FR-004** Every metric MUST carry provenance: source, retrieval timestamp, and
  a quality classification of `verified`, `estimated`, or `unavailable`.
- **FR-005** The system MUST display counts of: weeks loaded, weeks with a
  metrics bundle, weeks with a report pair, weeks with both, and weeks missing
  either.
- **FR-006** The page MUST assert its own invariants at load and MUST render a
  visible failure banner when an assertion fails, rather than degrading silently.

### 4.2 Ingestion

- **FR-010** The system MUST discover report pairs by globbing
  `weekly-report-YYYY-MM-DD.md` and `-personal.md` in the canonical report
  directory.
- **FR-011** The system MUST discover metrics bundles by globbing dated
  directories containing `weekly-metrics.json`.
- **FR-012** The system MUST reconcile the two sets by week-ending date and MUST
  classify each week as `pair+bundle`, `pair-only`, or `bundle-only`.
- **FR-013** The system MUST parse checkbox items from the personal report's
  `## Project Pipeline with Carry-Over` section, capturing checked state, item
  text, project heading, and any parenthetical carry-over annotation.
- **FR-014** The system MUST tolerate schema drift across bundles. Six bundles
  span three months and field sets differ; a missing field MUST yield `null`,
  never an exception that aborts ingestion.
- **FR-015** Ingestion MUST be read-only with respect to the report corpus. It
  MUST NOT modify, move, or rewrite any report.

### 4.3 Dark Work Accounting

- **FR-020** The system MUST compute sessions-per-commit per week and MUST
  present it as a first-class series alongside commit count.
- **FR-021** The system MUST record, per project per week, the count of
  uncommitted changes observed at collection time, so that work existing only as
  untracked files is represented.
- **FR-022** A week whose sessions-per-commit exceeds a configured threshold MUST
  be flagged, and the flag MUST state that commit-based metrics understate it.
- **FR-023** Where daily session counts are available, the system MUST render the
  intra-week distribution, because a week's shape distinguishes sustained work
  from a single burst.

### 4.4 Carry-Over Ledger

- **FR-030** The system MUST compute carry age for every unchecked item by
  matching item text across consecutive weeks using normalized comparison.
- **FR-031** The carry-over panel MUST sort by descending carry age.
- **FR-032** Items reaching a configured age threshold MUST be marked as
  stalled, with the recommendation to complete or retire made explicit.
- **FR-033** The system MUST show completion events: items that transitioned from
  `[ ]` to `[x]`, with the number of weeks they were carried before completion.
- **FR-034** Text matching MUST be conservative. An uncertain match MUST be
  reported as a separate item rather than silently merged, since a false merge
  understates carry age.

### 4.5 Visualization

- **FR-040** Every figure MUST be interactive: hover tooltips, legend toggling,
  and series focus.
- **FR-041** Hovering any point MUST bring its series into focus and dim the
  others, so overlapping points remain inspectable.
- **FR-042** Point labels MUST NOT overlap. Where density prevents clean
  labeling, labels MUST be suppressed in favor of hover disclosure rather than
  rendered illegibly.
- **FR-043** Figures MUST use the full available plotting area. A chart stranded
  in a corner, or dominated by whitespace from a single outlier, is a defect.
- **FR-044** Axes MUST be labeled with units. Any axis using a non-linear scale
  MUST state that scale.
- **FR-045** The system MUST NOT draw fitted curves, regression lines, or
  interpolated segments across missing weeks. Lines connect observed points only.
- **FR-046** Weeks with no data MUST render as a visible gap.

### 4.6 Report Integration

- **FR-050** The dashboard MUST render the current week's dad-facing and personal
  report text, since the figures show the pattern and the prose explains it.
- **FR-051** Any prior week MUST be selectable, updating both figures and prose.
- **FR-052** The dashboard MUST NOT restate report conclusions in its own words.
  It presents the reports; it does not summarize them.

### 4.7 Regeneration

- **FR-060** A single command MUST regenerate the dashboard from the corpus.
- **FR-061** Regeneration MUST be idempotent: unchanged inputs produce
  byte-identical output.
- **FR-062** The generator MUST exit non-zero when any invariant fails, so it can
  gate automation.
- **FR-063** The generator MUST report what it skipped and why. Silent truncation
  is prohibited.

## 5. Non-Functional Requirements

### 5.1 Performance
- **NFR-001** Full regeneration completes in under 30 seconds for 52 weeks.
- **NFR-002** The page reaches interactive state in under 2 seconds from local disk.
- **NFR-003** Total page weight stays under 3 MB including embedded assets.

### 5.2 Reliability
- **NFR-010** A malformed bundle MUST NOT abort the run; it is skipped, counted,
  and reported. This mirrors the `ld sync` defect of 2026-08-01, where one bad
  record aborted an entire corpus run and hid twenty finished artifacts.
- **NFR-011** The dashboard MUST render usefully from partial data.

### 5.3 Security
- **NFR-020** No network requests at runtime. A strict offline page cannot leak.
- **NFR-021** All report text MUST be escaped on injection into HTML.
- **NFR-022** No credentials, tokens, absolute home paths, or provider keys in
  output. The corpus contains operational detail not intended for publication.

### 5.4 Scalability
- **NFR-030** Correct behavior to at least 104 weeks without layout redesign.
- **NFR-031** Beyond the display window, older weeks remain in the canonical
  table and reachable by selector.

### 5.5 Accessibility
- **NFR-040** Dark mode is the default and primary target.
- **NFR-041** Text contrast meets WCAG AA.
- **NFR-042** Information MUST NOT be conveyed by color alone; series are also
  distinguished by marker shape or label.
- **NFR-043** Every figure has an adjacent data table conveying the same values.

## 6. Key Entities

**WeekRecord** -- one row per week-ending date. Fields: `week_ending`,
`period_start`, `period_end`, `has_pair`, `has_bundle`, `sessions`, `commits`,
`files_changed`, `projects_active`, `sessions_per_commit`, `uncommitted_changes`,
`momentum_score`, `dad_report_path`, `personal_report_path`, `dad_word_count`,
`agent_breakdown`, `daily_sessions`, `data_quality`, `missing_fields`,
`source_bundle`, `retrieved_at`.

**CarryOverItem** -- `item_text`, `normalized_text`, `project_heading`,
`first_seen_week`, `last_seen_week`, `carry_age`, `state`, `completed_week`,
`weeks_carried_before_completion`, `match_confidence`.

**ProjectWeekActivity** -- `week_ending`, `project_name`, `commits`,
`files_changed`, `uncommitted_count`, `state`.

**ValidationAssertion** -- `assertion_id`, `description`, `expected`, `actual`,
`passed`.

## 7. Success Criteria

- **SC-1** All 13 existing weeks appear in the trend view with correct
  classification of pair/bundle coverage.
- **SC-2** The four-week-old trend-comparison carry-over is displayed with carry
  age 4, and this project's completion closes it.
- **SC-3** The 2026-08-01 week is flagged as dark-work-heavy on the evidence that
  110 of 122 sessions produced no commits.
- **SC-4** Opening `index.html` with networking disabled yields full function.
- **SC-5** Regenerating twice without input changes produces identical bytes.
- **SC-6** Every displayed number traces to a source file, or is labeled
  unavailable.

## 8. Prior Art Analysis

### 8.1 Existing Solutions

| Solution | Assessment |
| --- | --- |
| Current `render_dashboard.py` | Renders one week per page. No cross-week view. Basis for ingestion logic; superseded for presentation. |
| `prometheus_exporter.py` + Grafana provisioning | Already present in the suite. User confirmed the pairing on 2026-05-19: "yes grafana was it - and prometheus is also correct". Correct for live operational metrics; wrong for a 13-week narrative history that must survive without a running service. |
| Grafana alone | Requires a running server and datasource. Fails the offline, self-contained, portable-artifact requirement. |
| Static site generator | Adds a build toolchain and dependency surface disproportionate to one page. |

### 8.2 Patterns Adopted

- **Canonical table first**, from the user's 2026-07-04 dashboard specification:
  "Build the canonical data table first. Derive every model list, chart,
  selector, frontier, role assignment, tooltip, count, and conclusion from that
  one table. Never maintain a separate hand-written model list."
- **Single self-contained dark-mode `index.html`**, same source: "there must not
  be a maze of supporting documents."
- **No invented values**, same source: missing stays missing and is labeled.
- **Self-validating page** that fails its own check when counts are wrong.
- **Isolate per-item failure** so one bad record cannot abort the corpus, from
  the `ld sync` defect of 2026-08-01.

### 8.3 Patterns Avoided

- **Fitted or smoothed trend lines.** Explicitly rejected by the user: "Do not
  draw a fitted curve. Do not draw a regression line."
- **Charts built before the data layer.** The 2026-07-03 complaint -- "the graphs
  are still not fixed! ... its hard as fuck to read" -- followed from charts
  drawn against ad hoc data.
- **Commit-count-only throughput**, which demonstrably misrepresents dark-work
  weeks.
- **A second task database.** The maintenance-reporting control-plane decision of
  2026-07-28 holds: Living Documents owns tasks; this is a projection.

## 9. Assumptions and Dependencies

### Assumptions
- Report filenames follow `weekly-report-YYYY-MM-DD[-personal].md`.
- The personal report retains its `## Project Pipeline with Carry-Over` section
  and `- [ ]` / `- [x]` convention.
- Week-ending dates are unique keys.
- The corpus stays on one machine; no multi-user concurrency.

### Dependencies
- Report corpus at `/home/cheta/code/weekly-reports/`.
- Metrics bundles at `/home/cheta/code/weekly-report-dashboard/`.
- `collect_weekly_evidence.py` continues to emit `weekly-metrics.json`.
- Python 3.11+ for the generator.
- No runtime service dependency by design.

## 10. Identified Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Carry-over text matching produces false merges | Understated carry age; the core metric becomes wrong | Conservative normalization; unmatched items stay separate; expose `match_confidence` |
| Bundle schema drift across three months | Ingestion crash or silent wrong values | Field-level tolerance, `null` on absent, per-week `missing_fields` |
| Uncommitted-work counts are collection-time snapshots | Historic weeks cannot be reconstructed | Record forward from now; label historic weeks `unavailable`, never zero |
| Corpus split across two directories | Weeks silently missing | Reconcile both, classify coverage, display gaps explicitly |
| Report prose contains sensitive operational detail | Leak if published | Local-only artifact; no network; path scrubbing before any sharing |
| Embedding a chart library inflates page weight | Slow load | Measure against the 3 MB budget; the library is the only large dependency |

## 11. Scope Boundaries

### In Scope
- Multi-week trend across the existing corpus
- Carry-over ledger with age tracking
- Dark-work accounting including uncommitted state
- Self-contained offline dark-mode HTML
- Idempotent single-command regeneration
- Current and historic report prose display
- Self-validating invariant assertions

### Out of Scope
- Writing or editing weekly reports (the suite skill owns that)
- Live or real-time metrics (Prometheus and Grafana own that)
- Multi-user hosting, authentication, or publication
- Replacing Living Documents as task authority
- Predictive forecasting of future weeks
- Mobile-first layout; desktop is the target surface

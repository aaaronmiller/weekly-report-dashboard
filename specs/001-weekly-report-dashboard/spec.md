# Feature Specification: Weekly Report Dashboard -- Trend and Carry-Over View

**Feature Branch**: `001-weekly-report-dashboard`

**Created**: 2026-08-01

**Status**: Ready for planning

**Input**: `specs/requirements.md`, `specs/design.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See throughput across every recorded week (Priority: P1)

As the workspace operator, I open one page and see how sessions, commits, files
changed, and active projects have moved across all thirteen recorded weeks, so I
can judge this week against a real baseline instead of an impression.

**Why this priority**: This is the four-week-deferred carry-over item and the
reason the project exists. Without it there is no trend, and every other view is
an enhancement to something that does not yet work. It is independently
valuable: the trend alone answers "is throughput rising or falling".

**Independent Test**: Build against the real corpus and confirm all thirteen
week-ending dates appear in the time series in date order, each labeled, with
the current week marked.

**Acceptance Scenarios**:

1. **Given** 12 report pairs and 6 metrics bundles, **When** the dashboard is
   generated, **Then** the canonical table contains 12 week records, each
   classified `pair+bundle`, `pair-only`, or `bundle-only`.
2. **Given** a week with no metrics bundle, **When** the trend renders, **Then**
   that week appears as a visible gap and is never interpolated or omitted.
3. **Given** the canonical table, **When** the page loads, **Then** the table is
   displayed before the figures, searchable and sortable.
4. **Given** any rendered figure, **When** the user hovers a point, **Then** that
   series comes into focus, the others dim, and the tooltip states the week,
   value, source, and data quality.

---

### User Story 2 - Expose work that commit counts cannot see (Priority: P1)

As the workspace operator, I need weeks whose effort produced no commits to be
visible and flagged, so that the dashboard does not silently understate them.

**Why this priority**: Equal to US1 because the trend is actively misleading
without it. The 2026-08-01 week recorded 23 commits while its largest
deliverable, nine modules with 174 passing tests, was untracked. A trend chart
showing only commits reports that week as ordinary. It was not.

**Independent Test**: Load the 2026-08-01 fixture and confirm the week is flagged
as dark-work-heavy with sessions-per-commit computed from 122 sessions and 23
commits, and that the flag states commit metrics understate the week.

**Acceptance Scenarios**:

1. **Given** a week with 122 sessions and 23 commits, **When** the dark-work
   figure renders, **Then** sessions-per-commit appears as its own series and the
   week is flagged against the configured threshold.
2. **Given** a flagged week, **When** the user inspects the flag, **Then** it
   states explicitly that commit-based metrics understate that week.
3. **Given** a project with uncommitted changes at collection time, **When** the
   project activity figure renders, **Then** the uncommitted count is shown
   alongside the commit count.
4. **Given** a week predating uncommitted-state collection, **When** that week
   renders, **Then** its uncommitted count is `unavailable`, never `0`.
5. **Given** daily session counts, **When** a week is selected, **Then** the
   intra-week distribution renders, distinguishing sustained work from one burst.

---

### User Story 3 - Age every carried commitment (Priority: P2)

As the workspace operator, I want each unchecked item to show how many
consecutive weeks it has been carried, so that chronically deferred work becomes
undeniable rather than quietly repeating.

**Why this priority**: High value but depends on the data layer from US1. The
corpus already proves the need: the trend-comparison item has been carried four
weeks and the oh-my-pi research item four weeks, and neither is visible as
stalled in any single week's report.

**Independent Test**: Parse all personal reports and confirm the
week-over-week trend item reports carry age 4 and sorts above younger items.

**Acceptance Scenarios**:

1. **Given** an item unchecked in four consecutive personal reports, **When** the
   ledger renders, **Then** it shows carry age 4.
2. **Given** items of differing ages, **When** the ledger renders, **Then** they
   sort by descending carry age.
3. **Given** an item at or beyond the stall threshold, **When** it renders,
   **Then** it is marked stalled with complete-or-retire made explicit.
4. **Given** an item that went from `[ ]` to `[x]`, **When** the ledger renders,
   **Then** it appears as a completion with the number of weeks carried.
5. **Given** two items whose text differs beyond normalization, **When** matching
   runs, **Then** they remain separate and are marked `uncertain` rather than
   merged.

---

### User Story 4 - Read the prose beside the numbers (Priority: P3)

As the workspace operator, I want the selected week's dad-facing and personal
reports rendered in the page, because the figures show the pattern and the prose
explains what it meant.

**Why this priority**: Genuinely useful but the dashboard delivers value without
it; the reports remain readable as files.

**Independent Test**: Select any week and confirm both reports render with
correct headings, tables, and checkboxes, and that switching weeks updates both.

**Acceptance Scenarios**:

1. **Given** a selected week with a pair, **When** the prose panel renders,
   **Then** both reports display with headings, tables, lists, and checkboxes
   intact.
2. **Given** a selected week, **When** the user changes selection, **Then**
   figures 3 and 4 and the prose all update together.
3. **Given** report text containing HTML or Markdown special characters, **When**
   it renders, **Then** it is escaped and displays literally.
4. **Given** any report, **When** it renders, **Then** absolute home paths appear
   scrubbed to `~`.

---

### User Story 5 - Trust the artifact (Priority: P2)

As the workspace operator, I need the page to declare its own coverage and fail
visibly when its invariants break, so I can tell at a glance whether what I am
reading is complete.

**Why this priority**: Cheap to build once the data layer exists, and it is what
separates this from the artifacts that previously looked right while being wrong.

**Independent Test**: Corrupt one bundle, rebuild, and confirm the run completes,
the bad week is named with a reason, the coverage panel counts it, and `--check`
exits non-zero.

**Acceptance Scenarios**:

1. **Given** a malformed bundle, **When** the generator runs, **Then** it
   completes, skips that week, names it with a reason, and does not abort.
2. **Given** the page loads, **When** an assertion fails, **Then** a visible
   failure banner renders naming the failed assertion.
3. **Given** any build, **When** it finishes, **Then** the page displays weeks
   loaded, with pair, with bundle, with both, and missing.
4. **Given** unchanged inputs, **When** the generator runs twice, **Then** the
   outputs are byte-identical.
5. **Given** networking is disabled, **When** `index.html` is opened from disk,
   **Then** every figure, tooltip, legend toggle, and selector functions.

---

---

### User Story 6 - Regenerate on a schedule without being asked (Priority: P2)

As the workspace operator, I want daily and weekly dashboard regeneration to run
on a schedule from the CLI, so the view is current when I open it rather than
current only when I remember to rebuild it.

**Why this priority**: Recovered directive, 2026-05-28: *"Add a cronjob
scheduling feature in TUI, GUI, and CLI for auto deployment of daily and weekly
versions."* This was recorded two months before the specification was written and
was omitted from it. A dashboard that must be rebuilt by hand goes stale exactly
when attention is elsewhere, which is the condition it exists to detect.

Scope is narrowed deliberately: this feature covers the **CLI** path only. The
TUI and GUI surfaces named in the original directive belong to whatever owns
those surfaces, and claiming them here would overstate what this project builds.

**Independent Test**: Install the schedule, wait for one interval, and confirm
`index.html` was rebuilt with no human action and the run was logged.

**Acceptance Scenarios**:

1. **Given** the generator is installed, **When** the user runs the schedule
   install command, **Then** a recurring job is registered for the daily and
   weekly cadences and its identity and next run time are printed.
2. **Given** a scheduled run fires, **When** it completes, **Then** the outcome,
   duration, and any skipped weeks are appended to a run log.
3. **Given** a scheduled run fails an assertion, **When** it exits, **Then** the
   failure is recorded and the previously good `index.html` is left in place
   rather than replaced with a broken one.
4. **Given** a schedule is already installed, **When** install runs again,
   **Then** it is idempotent and does not create a duplicate job.
5. **Given** the user runs the uninstall command, **Then** the job is removed and
   its absence is confirmed.

---

### User Story 7 - Reports carry work, not process talk (Priority: P3)

As the workspace operator, I want the prose the dashboard surfaces to exclude
process meta-discussion and to preserve job-search and meetup references, so what
is displayed is the work rather than the conversation about the work.

**Why this priority**: Recovered directive, 2026-07-20: *"Redo daily report
excluding process meta-discussion, include more job search references and meetup
references."* The specification treats reports as read-only input and never
addresses what they should contain, so this directive had no home.

**Independent Test**: Render a week whose report contains both a process aside
and a job-search item; confirm the aside is de-emphasised, the job-search item is
retained, and the source Markdown is unmodified.

**Acceptance Scenarios**:

1. **Given** a report containing process meta-discussion, **When** the prose
   panel renders, **Then** those passages are marked as process rather than
   silently deleted, because the corpus is the record and deletion is loss.
2. **Given** a report containing job-search or meetup references, **When** it
   renders, **Then** those are preserved and surfaced, never filtered as noise.
3. **Given** any classification is applied, **When** the panel renders, **Then**
   it states how many passages were classified and by what rule, so the
   filtering is auditable rather than invisible.
4. **Given** the corpus is read, **When** anything renders, **Then** the source
   Markdown is unchanged: classification is a display decision only.

### Edge Cases

- A week with a bundle but no report pair, or a pair but no bundle.
- A week with zero commits: sessions-per-commit is `null`, not infinity.
- A personal report with no `Project Pipeline with Carry-Over` section.
- A checkbox item whose text changes slightly between weeks.
- An item that goes unchecked, checked, then unchecked again.
- Bundles whose schemas differ across three months of format drift.
- A duplicate week-ending date across the two source directories.
- A report containing a Markdown table with pipe characters inside cells.
- Corpus larger than the display window (beyond 52 weeks).
- The very first week, which has no prior week to compare against.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST build one canonical table before rendering any figure,
  and every displayed value MUST derive from it.
- **FR-002**: System MUST display the canonical table, searchable and sortable,
  before the analytical figures.
- **FR-003**: System MUST keep missing values null and MUST NOT coerce them to
  zero.
- **FR-004**: System MUST attach source, retrieval timestamp, and quality
  classification to every metric.
- **FR-005**: System MUST display coverage counts for weeks loaded, with pair,
  with bundle, with both, and missing.
- **FR-006**: System MUST assert its own invariants at load and render a visible
  failure banner when one fails.
- **FR-010**: System MUST discover report pairs and metrics bundles and reconcile
  them by week-ending date.
- **FR-013**: System MUST parse checkbox items from the personal report's
  carry-over section with their state and owning project.
- **FR-014**: System MUST tolerate bundle schema drift, yielding null for absent
  fields rather than raising.
- **FR-015**: System MUST treat the report corpus as read-only.
- **FR-020**: System MUST compute and display sessions-per-commit as a
  first-class series.
- **FR-021**: System MUST record per-project uncommitted change counts at
  collection time.
- **FR-022**: System MUST flag weeks exceeding the dark-work threshold and state
  that commit metrics understate them.
- **FR-023**: System MUST render intra-week daily session distribution where
  available.
- **FR-030**: System MUST compute carry age for every unchecked item.
- **FR-031**: System MUST sort the carry-over ledger by descending carry age.
- **FR-032**: System MUST mark items at the stall threshold and state
  complete-or-retire.
- **FR-033**: System MUST show completions with weeks carried before completion.
- **FR-034**: System MUST keep uncertain text matches separate rather than
  merging them.
- **FR-041**: System MUST focus a hovered series and dim the others.
- **FR-042**: System MUST prevent overlapping point labels, preferring hover
  disclosure over illegible rendering.
- **FR-045**: System MUST NOT draw fitted curves, regression lines, or
  interpolation across missing weeks.
- **FR-046**: System MUST render weeks with no data as visible gaps.
- **FR-050**: System MUST render the selected week's dad and personal reports.
- **FR-051**: System MUST allow selecting any prior week, updating figures and
  prose together.
- **FR-060**: System MUST regenerate from a single command.
- **FR-061**: Regeneration MUST be idempotent.
- **FR-062**: Generator MUST exit non-zero on any failed assertion.
- **FR-063**: Generator MUST report what it skipped and why.
- **NFR-020**: System MUST make no network request at runtime.
- **NFR-021**: System MUST escape all corpus text before HTML injection.
- **NFR-022**: System MUST scrub home paths and MUST NOT emit credentials.
- **NFR-042**: System MUST NOT convey information by color alone.
- **NFR-043**: Every figure MUST have an adjacent data table.

- **FR-070**: System MUST provide a CLI command to install a recurring
  regeneration schedule for daily and weekly cadences.
- **FR-071**: Schedule installation MUST be idempotent and MUST NOT create
  duplicate jobs on repeat invocation.
- **FR-072**: System MUST provide a CLI command to uninstall the schedule and
  confirm its removal.
- **FR-073**: Each scheduled run MUST append its outcome, duration, and skipped
  items to a run log.
- **FR-074**: A scheduled run that fails an assertion MUST leave the previous
  `index.html` in place rather than overwrite it with a failed build.
- **FR-080**: System MUST classify report passages as process meta-discussion
  without deleting them, marking rather than removing.
- **FR-081**: System MUST preserve and surface job-search and meetup references.
- **FR-082**: System MUST state how many passages were classified and by which
  rule.
- **FR-083**: Classification MUST NOT modify the source Markdown.

### Key Entities

- **WeekRecord**: One per week-ending date. Throughput counts, coverage flags,
  report paths, agent and daily breakdowns, provenance, and explicit
  `missing_fields`.
- **CarryOverItem**: A commitment tracked across weeks. Original and normalized
  text, owning project, first and last seen, carry age, state, completion week,
  and match confidence.
- **ProjectWeekActivity**: Per project per week commits, files changed, and
  uncommitted count.
- **ValidationAssertion**: Assertion id, description, expected, actual, passed.
  Emitted into the page as data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 12 existing weeks appear in the trend with correct coverage
  classification.
- **SC-002**: The week-over-week trend carry-over displays carry age 4, and
  shipping this feature closes it.
- **SC-003**: The 2026-08-01 week is flagged dark-work-heavy on the evidence that
  110 of 122 sessions produced no commits.
- **SC-004**: `index.html` opens from disk with networking disabled and is fully
  functional.
- **SC-005**: Two consecutive runs over unchanged input produce byte-identical
  output.
- **SC-006**: Every displayed number traces to a source file or is labeled
  unavailable.
- **SC-007**: A corrupted bundle does not prevent the other 12 weeks from
  rendering.
- **SC-008**: Full regeneration of 52 weeks completes in under 30 seconds.
- **SC-009**: Page weight stays under 3 MB and reaches interactive in under 2
  seconds from disk.

- **SC-010**: A scheduled run regenerates `index.html` with no human action and
  records the run in the log.
- **SC-011**: A week containing both a process aside and a job-search reference
  renders with the aside marked and the reference retained.

## Assumptions

- Report filenames follow `weekly-report-YYYY-MM-DD[-personal].md`.
- The personal report keeps its `## Project Pipeline with Carry-Over` section and
  `- [ ]` / `- [x]` convention.
- Week-ending dates uniquely identify a week.
- `collect_weekly_evidence.py` continues to emit `weekly-metrics.json`.
- Uncommitted-state history cannot be reconstructed; it is recorded from now
  forward and labeled unavailable for prior weeks.
- Desktop browser is the target surface.
- Single machine, single user, no concurrent writers.

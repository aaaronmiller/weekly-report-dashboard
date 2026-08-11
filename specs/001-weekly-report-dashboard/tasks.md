---
description: "Task list for Weekly Report Dashboard -- Trend and Carry-Over View"
---

# Tasks: Weekly Report Dashboard -- Trend and Carry-Over View

**Input**: Design documents from `/specs/001-weekly-report-dashboard/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included. The specification defines testable invariants (SC-005,
SC-007) that cannot be verified by inspection, and the constitution makes
assertion gating non-negotiable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Owning user story
- Paths are relative to `/home/cheta/code/weekly-report-dashboard/`

## Critical ordering constraint

**Phase 3 must not begin until Phase 1 is complete and its tests pass.**

Constitution Principle I forbids writing chart code before the canonical table
is assembled, validated, and printed. This is the one ordering rule that may not
be relaxed for convenience; it is the rule whose violation caused every prior
dashboard failure in this workspace.

---

## Phase 1: Data Layer (Foundation — blocks everything else)

- [x] T001 [P] Create `scripts/models.py` with dataclasses `WeekRecord`,
      `CarryOverItem`, `ProjectWeekActivity`, `ValidationAssertion` exactly as
      specified in data-model.md. All optional fields typed `X | None` with
      default `None`. `missing_fields` defaults to an empty list, never `None`.

- [x] T002 [P] Create `tests/conftest.py` with fixtures pointing at the real
      corpus (`/home/cheta/code/weekly-reports`,
      `/home/cheta/code/weekly-report-dashboard`) plus a `tmp_path` fixture that
      builds a synthetic 3-week corpus for isolated tests.

- [x] T003 Implement `discover_reports(dir)` in `scripts/ingest.py`. Glob
      `weekly-report-YYYY-MM-DD.md` and `-personal.md`, pair by date, return
      `(dict[date, ReportPair], problems)`. Must never raise on a malformed
      filename; it records a problem and continues.

- [x] T004 Implement `discover_bundles(dir)` in `scripts/ingest.py`. Glob dated
      directories containing `weekly-metrics.json`. Return
      `(dict[date, dict], problems)`. A JSON parse error yields a problem
      record, not an exception (FR-014, NFR-010).

- [x] T005 Implement `parse_carry_over(personal_md)` in `scripts/ingest.py`.
      Extract from `## Project Pipeline with Carry-Over`: checked state, item
      text, and owning project heading. Handle absent section by returning an
      empty list plus a problem note.

- [x] T006 Implement `collect_git_state(project_dirs)` in `scripts/ingest.py`.
      Run `git status --porcelain` read-only per project, return per-project
      uncommitted counts. Timeout-bounded; a failing repo yields `None`, not `0`
      (FR-021, Principle II).

- [x] T007 [P] Write `tests/test_ingest.py`: report pairing, bundle schema drift
      across the 6 real bundles, checkbox parsing including malformed lines,
      missing carry-over section, and the assertion that a corrupt bundle
      produces a problem record rather than an exception.

- [x] T008 Implement `normalize_item(text)` in `scripts/canonicalize.py` per the
      normalization rule in data-model.md: lowercase, strip trailing
      parenthetical, collapse whitespace, strip edge punctuation.

- [x] T009 Implement `build_week_records(reports, bundles, git)` in
      `scripts/canonicalize.py`. Reconcile by week-ending date, set `coverage`,
      compute `sessions_per_commit` as `None` when commits is `None` **or zero**,
      populate `missing_fields`, and attach provenance (`source_bundle`,
      `retrieved_at`, `data_quality`).

- [x] T010 Implement `build_carry_over_ledger(reports)` and
      `compute_carry_age(items)` in `scripts/canonicalize.py`. Carry age counts
      **consecutive** unchecked appearances and restarts after a completion.
      Uncertain matches stay separate and are labeled `uncertain` (FR-034).

- [x] T011 Implement `build_project_activity(bundles, git)` in
      `scripts/canonicalize.py`, producing `ProjectWeekActivity` rows.

- [x] T012 [P] Write `tests/test_canonicalize.py`: normalization strips the
      `(carry-over from Jul 11, Jul 19)` form; carry age across consecutive and
      non-consecutive weeks; unchecked→checked→unchecked restarts age;
      `sessions_per_commit` is `None` at zero commits, never infinity;
      `uncommitted_changes` is `None` and never `0` for historic weeks.

- [x] T013 Implement `scripts/validate.py` returning `list[ValidationAssertion]`
      for A-001 through A-007 in data-model.md. Assertions are returned as data;
      the module never raises on a failed assertion.

- [x] T014 [P] Write `tests/test_validate.py`: each assertion passes on the real
      corpus, and each fails when its precondition is deliberately broken.

- [x] T015 Create `scripts/build_dashboard.py` entry point wiring ingest →
      canonicalize → validate. Implement `--check`, the exit codes in
      contracts/cli.md, and the stdout contract including every skipped item with
      its reason (FR-062, FR-063).

**Gate 1**: `python3 scripts/build_dashboard.py --check` runs against the real
corpus, reports 12 weeks with correct coverage classification, all assertions
pass, exit code 0, and no file in the corpus is modified.

---

## Phase 2: Static Emission (US5 — trust the artifact)

- [x] T016 [P] [US5] Create `assets/dashboard.css`: dark theme, WCAG AA contrast,
      layout for header, canonical table, figure slots, ledger, prose panel.

- [x] T017 [US5] Implement `escape_html(text)` and `scrub_paths(text)` in
      `scripts/emit.py`. Escaping happens before any injection; `/home/<user>`
      becomes `~` (NFR-021, NFR-022).

- [x] T018 [US5] Implement the restricted Markdown renderer in `scripts/emit.py`:
      headings, paragraphs, tables, checkboxes, bold, code spans. Input is
      escaped first, so source HTML renders literally and cannot execute (R-4).

- [x] T019 [US5] Implement `serialize_payload(canonical, assertions)` in
      `scripts/emit.py` producing `window.__WEEKLY__` per
      contracts/embedded-data.md. Use
      `json.dumps(..., sort_keys=True, separators=(",", ":"), default=str)`.
      Derive `generated_at` from the newest input mtime, not wall-clock (R-7).

- [x] T020 [US5] Implement `render(canonical, assertions, out_dir)` in
      `scripts/emit.py` writing a single `index.html` with CSS and payload
      inlined. Include header with coverage counts, the searchable sortable
      canonical table, and the failure banner element.

- [x] T021 [US5] Implement client-side table search and sort in `assets/dashboard.js`,
      operating over `window.__WEEKLY__.weeks` without mutating it (FR-002).

- [x] T022 [US5] Implement the validation failure banner in `assets/dashboard.js`:
      read `assertions`, render a visible banner naming each failed assertion
      (FR-006). The page must not re-derive assertions.

- [x] T023 [P] Write `tests/test_emit.py`: escaping of HTML and Markdown special
      characters, path scrubbing, payload sorts keys, nulls serialize as `null`
      and never `0`.

- [x] T024 [P] Write `tests/test_integration.py::test_idempotence`: two
      consecutive builds produce byte-identical `index.html` (SC-005).

- [x] T025 [P] Write `tests/test_integration.py::test_malformed_bundle`: inject a
      corrupt bundle, assert the run completes, that week is named as skipped
      with a reason, and the remaining 12 weeks still render (SC-007).

**Gate 2**: `index.html` opens from disk with networking disabled, shows the
canonical table and correct coverage counts, and rebuilds byte-identically.

---

## Phase 3: Figures (US1, US2 — trend and dark work)

**Do not start until Gate 1 has passed.**

- [x] T026 Vendor ECharts 5.x minified into `vendor/echarts.min.js`. Record the
      exact version and a SHA-256 checksum in `vendor/README.md`. Never fetched
      at runtime (TDR-002).

- [x] T027 Implement chart base configuration in `assets/dashboard.js`: dark
      theme, and for every series
      `emphasis: {focus:'series', blurScope:'coordinateSystem'}`,
      `labelLayout: {hideOverlap:true}`, `connectNulls: false`. These three
      settings implement FR-041, FR-042, and FR-046 respectively.

- [x] T028 [US1] Implement Figure 1, throughput trend: sessions, commits, files
      changed, active projects across all weeks. Weeks lacking data render as
      visible gaps, never interpolated. Current week marked distinctly.

- [x] T029 [US1] Add the Figure 1 data table beneath the chart carrying the same
      values (NFR-043), and vary marker shape as well as color so no information
      is conveyed by color alone (NFR-042).

- [x] T030 [US2] Implement Figure 2, dark work: `sessions_per_commit` as its own
      series with the threshold band drawn. Flagged weeks annotated with text
      stating that commit-based metrics understate them.

- [x] T031 [US2] Implement Figure 3, intra-week distribution: daily sessions for
      the selected week from `daily_sessions`.

- [x] T032 [US2] Implement Figure 4, project activity: commits and uncommitted
      counts per project for the selected week. Historic weeks show uncommitted
      as `unavailable`, never `0`.

- [x] T033 Implement tooltips across all figures showing week, value, source,
      retrieval time, and data quality (FR-004).

- [x] T034 [P] Write `tests/test_integration.py::test_dark_work_fixture`: build
      against the real corpus and assert the 2026-08-01 week is flagged with 122
      sessions and 23 commits (SC-003). This is a permanent regression fixture.

**Gate 3**: AS-1 through AS-4 demonstrable in the browser; 2026-08-01 visibly
flagged; hovering a series dims the others; no overlapping labels.

---

## Phase 4: Carry-Over Ledger and Prose (US3, US4)

- [x] T035 [US3] Implement the carry-over ledger panel in
      `assets/dashboard.js`: open items sorted by descending carry age, stalled
      items marked with complete-or-retire stated explicitly (FR-031, FR-032).

- [x] T036 [US3] Add the completions view: items that reached `[x]` with the
      number of weeks carried before completion (FR-033).

- [x] T037 [US3] Surface `match_confidence` in the ledger so `uncertain` items
      are visibly not merged (FR-034).

- [x] T038 [P] Write `tests/test_integration.py::test_carry_age_fixture`: assert
      the week-over-week trend item reports carry age 4 (SC-002). This is the
      project's own regression fixture.

- [x] T039 [US4] Implement the week selector control updating Figures 3 and 4
      and the prose panel together (FR-051).

- [x] T040 [US4] Implement the prose panel rendering the selected week's dad and
      personal reports through the restricted Markdown renderer (FR-050).

- [x] T041 [US5] Implement the coverage and provenance panel listing weeks missing a
      pair or bundle with the reason (FR-005).

**Gate 4**: Trend item shows carry age 4; prose renders escaped and scrubbed;
week selection updates figures and prose together.

---

## Phase 5: Integration and Retirement

- [x] T042 Add `--weeks`, `--dark-work-threshold`, and `--stall-age` flags per
      contracts/cli.md, threading them into `config` in the embedded payload.

- [x] T043 Verify performance: full build under 30 seconds and page weight under
      3 MB (SC-008, SC-009). Record measured values in `vendor/README.md`.

- [x] T044 Visual verification: open the rendered page and inspect it as an
      image. Confirm no overlapping labels, no chart stranded in a corner, no
      invisible points, no whitespace dominated by one outlier. DOM inspection
      and passing tests do not satisfy this task.

- [x] T045 Wire the generator into `weekly-report-suite/SKILL.md` as the
      dashboard step, replacing the `render_dashboard.py` invocation.

- [x] T046 Retire `custom-skills/weekly-report-suite/scripts/render_dashboard.py`
      with a note in the suite skill pointing at this generator. Do not delete
      historic per-week bundles.

- [x] T047 Update `/home/cheta/LIVING_DOCUMENTS/projects/weekly-reports/` to
      record that the week-over-week trend item is closed, using `ld add-page`
      rather than a direct file write.

- [x] T048 Consolidate the stray `weekly-report-2026-07-05` pair from
      `/home/cheta/code/` into `/home/cheta/code/weekly-reports/` so the corpus
      lives in one place (R-8). Copy, verify by checksum, then remove.

**Gate 5**: One command regenerates the dashboard from a clean checkout; the
suite skill invokes it; the single-week renderer is retired.

---

## Dependencies

```
T001, T002  ──→  T003..T006  ──→  T008..T011  ──→  T013  ──→  T015  ──→ GATE 1
                                                                          │
                                    ┌─────────────────────────────────────┤
                                    ▼                                     ▼
                          T016..T022 ──→ GATE 2                T026, T027 ──→ T028..T033 ──→ GATE 3
                                    │                                     │
                                    └──────────────┬──────────────────────┘
                                                   ▼
                                         T035..T041 ──→ GATE 4
                                                   ▼
                                         T042..T048 ──→ GATE 5
```

- T007, T012, T014, T023, T024, T025, T034, T038 are test tasks marked `[P]`;
  each may run in parallel with its siblings once its subject exists.
- T026 (vendoring) has no code dependency and may be done at any time, but
  Phase 3 chart work must still wait on Gate 1.

## Parallel execution opportunities

| Batch | Tasks | Reason |
| --- | --- | --- |
| A | T001, T002 | Different files, no shared state |
| B | T003, T004, T005, T006 | Independent readers in `ingest.py`; coordinate on one file |
| C | T007, T012, T014 | Independent test modules |
| D | T016, T026 | CSS and vendoring touch nothing shared |
| E | T023, T024, T025 | Independent test cases |

---

## Phase 6: Scheduled Regeneration (US6) and Report Curation (US7)

Added 2026-08-05 after cross-referencing the intent archaeology corpus. Both
directives predate the specification and were absent from it: scheduled
deployment was recorded 2026-05-28, report curation 2026-07-20.

- [x] T049 [US6] Implement `scripts/schedule.py` with `install`, `uninstall` and
      `status` subcommands, registering daily and weekly cadences through the
      platform scheduler. Install is idempotent: re-running never creates a
      second job (FR-070, FR-071, FR-072).

- [x] T050 [US6] Implement run logging in `scripts/schedule.py`: each scheduled
      run appends outcome, duration, and every skipped week with its reason to
      `run-log.jsonl` (FR-073).

- [x] T051 [US6] Make a failing scheduled run non-destructive. Build to a
      temporary path and promote only on success, so a run that fails an
      assertion leaves the previous `index.html` untouched (FR-074).

- [x] T052 [P] [US6] Write `tests/test_schedule.py`: install is idempotent,
      uninstall removes the job, a failing build leaves the prior artifact in
      place, and the run log records a skipped week with its reason.

- [x] T053 [US7] Implement `classify_passages()` in `scripts/curate.py`. Marks
      process meta-discussion; never deletes. Returns passage plus label plus
      the rule that fired, so every decision is attributable (FR-080).

- [x] T054 [US7] Implement job-search and meetup retention in
      `scripts/curate.py`. These are always preserved and surfaced, and are
      never eligible for the process classifier (FR-081).

- [x] T055 [US7] Surface the classification summary in the prose panel: how many
      passages were classified and by which rule (FR-082).

- [x] T056 [P] [US7] Write `tests/test_curate.py`: process asides are marked and
      not removed, job-search references survive classification, the summary
      count matches the labels applied, and the source Markdown is byte-identical
      before and after (FR-083).

**Gate 6**: A scheduled run regenerates the dashboard unattended and logs it
(SC-010). A week containing both a process aside and a job-search reference
renders with the aside marked and the reference retained (SC-011). No source
Markdown is modified by either feature.

## Traceability

Every requirement and success criterion maps to at least one task. A delegated
implementer can verify coverage from this table without re-reading the spec.

| Requirement | Tasks |
| --- | --- |
| FR-001 canonical table first | T009, T011, and the Phase 1 to 3 ordering gate |
| FR-002 table displayed, searchable, sortable | T020, T021 |
| FR-003 missing stays null | T001, T009, T023 |
| FR-004 provenance on every metric | T009, T033 |
| FR-005 coverage counts displayed | T020, T041 |
| FR-006 self-validating with failure banner | T013, T022 |
| FR-010 discover and reconcile by date | T003, T004, T009 |
| FR-013 parse carry-over checkboxes | T005 |
| FR-014 tolerate bundle schema drift | T004, T007 |
| FR-015 corpus is read-only | T003-T006, Gate 1 |
| FR-020 sessions-per-commit series | T009, T030 |
| FR-021 per-project uncommitted counts | T006, T011, T032 |
| FR-022 flag dark-work weeks | T030, T034 |
| FR-023 intra-week distribution | T031 |
| FR-030 carry age computed | T010 |
| FR-031 ledger sorted by age | T035 |
| FR-032 stalled items marked | T035 |
| FR-033 completions with weeks carried | T036 |
| FR-034 uncertain matches stay separate | T010, T037 |
| FR-041 hover focuses series | T027 |
| FR-042 no overlapping labels | T027, T044 |
| FR-045 no fitting or interpolation | T027, T028 |
| FR-046 gaps for missing weeks | T027, T028 |
| FR-050 render report prose | T040 |
| FR-051 week selector updates all | T039 |
| FR-060 single command | T015 |
| FR-061 idempotent output | T019, T024 |
| FR-062 non-zero exit on failure | T015 |
| FR-063 report what was skipped | T015 |
| NFR-020 no runtime network | T026, T044 |
| NFR-021 escape corpus text | T017, T023 |
| NFR-022 scrub paths, no secrets | T017, T023 |
| NFR-042 not color alone | T029 |
| NFR-043 data table per figure | T029 |
| SC-001 12 weeks classified | Gate 1, T009 |
| SC-002 trend item at carry age 4 | T038 |
| SC-003 2026-08-01 flagged | T034 |
| SC-004 offline function | Gate 2, T044 |
| SC-005 byte-identical rebuild | T019, T024 |
| SC-006 every number traceable | T033, T041 |
| SC-007 corrupt bundle isolated | T025 |
| SC-008 build under 30s | T043 |
| SC-009 under 3 MB, interactive under 2s | T043 |

## Definition of done

- All five gates passed.
- `python3 -m pytest tests/ -q` green.
- `python3 scripts/build_dashboard.py --check` exits 0.
- Page verified offline **and** visually inspected as an image.
- The week-over-week trend carry-over is closed, which is the outcome that
  justified the project.

# Specification Analysis Report — 001-weekly-report-dashboard + Template correlation

Generated: 2026-08-15 | Analyzer: speckit-analyze protocol (read-only)

## Pre-Checks
- Feature branch: `001-weekly-report-dashboard` (checked via tasks.md header; `.specify/scripts` branch check skipped for `main` — analysis proceeds read-only).
- Files present: `specs/001-weekly-report-dashboard/spec.md`, `plan.md`, `tasks.md`, `data-model.md`, `research.md`, `contracts/`, `quickstart.md`, `.specify/memory/constitution.md` (7 principles).

---

## Findings (high-signal, 10/3/1 iso applied per category)

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Constitution | **CRITICAL** if relaxed | `tasks.md:22-25` + `spec.md` gate1 | Phase 3 chart code before Phase 1 canonical table: tasks correctly gate it (T015 after T013), but template historically shipped chart before table (prior failures). | Enforce gate in CI: `python scripts/build_dashboard.py --check` must pass before any `assets/` change merges. Fresh v2 must not copy old `index.html` before regenerating from spec. |
| C2 | Constitution | HIGH | `spec.md: Acceptance Scenarios` | Principle II “Missing Is Not Zero” mapped to FR-021 etc.; `uncommitted_changes=None` not 0 is in data-model.md but tasks T012 tests only historic weeks, not boundary where git collector times out (returns None). | Add T012 case: `collect_git_state` timeout → `uncommitted_changes=None` + problem entry, not silent 0. Already implied, needs explicit test. |
| U1 | Underspec | MEDIUM | `spec.md: User Story 1 #3` | “table displayed before figures, searchable and sortable” — sort key undefined (by date vs sessions?). Plan says date order, spec says searchable/sortable without column list. | In spec acceptance: list columns and default sort (week_ending desc). Template `index.md` table currently date-sorted; keep invariant. |
| U2 | Underspec | MEDIUM | `spec.md: SC-005, SC-007` | Per tasks.md intro: SC-005/SC-007 are testable invariants not verifiable by inspection, but spec.md SC list not quoted verbatim — trace gap. | Pull SC-005 (`--check` prints coverage) and SC-007 (`--check` exits non-zero on assertion) into spec SC table explicitly, reference data-model invariants. |
| A1 | Ambiguity | MEDIUM | `spec.md: User Story 2 acceptance` | “flag states commit metrics understate the week” — wording allows either badge text or separate series; plan implements `sessions_per_commit` series + dark-work flag. Both interpretations satisfied, but wording is loose. | Keep plan’s dual (flag + SPC series); tighten spec future sentence: “Renders dark-work flag and SPC series where commits null-or-zero → SPC null.” |
| D1 | Duplication | LOW | `template/resources.md` vs `specs/weekly-report-dashboard` | Predecessor list in template resources overlaps gateway fidelity topics in spec research → acceptable dedup via linking, not copy. | No action — keep single source via `related:` links. |
| I1 | Inconsistency | HIGH | `spec.md: 13 weeks` vs `plan.md: thirteen-week corpus` vs live corpus 36 weeks | Spec fixture is 13-week historical set (gate 1), plan Summary says 13-week corpus, but `weekly-report-dashboard/telemetry.json` and `template/partials` note “36 weeks” live corpus. Terminology drift: fixture vs live. | Clarify in spec: “Gate 1 fixture = 13 weeks (historical); live corpus = 36 weeks as of 2026-08.” Update plan Summary footnote; tasks T007 bundle drift covers it. |
| G1 | Coverage Gap | HIGH | `tasks.md` Phase 6 — no task maps to SC requiring `<30s for 52 weeks` | Performance goal in plan Technical Context (`<30s for 52 weeks`) has no task ID. NFR-019? is in spec but no Txxx. | Add T0xx or tie to `scripts/build_dashboard.py` gate 6 `python -m pytest` timing assert; or mark as NFR without buildable work (but spec says NFRs need tasks). |
| G2 | Coverage Gap | MEDIUM | `spec.md: User Story 5 trust the artifact` | `validate.py` assertions A001-A007 each have T013/T014, but spec “trust” story expects visible failure banner — emit task exists (T018-T023) but mapping not explicit via [US5] tag. | Annotate emit tasks with `[US5]` where missing (T018 already has, ensure T022 banner is [US5]). |
| I2 | Inconsistency | LOW | `data-model.md` vs `template/intent-archaeology-findings.md` | Data model `missing_fields` never null aligns with findings page “missing_fields empty list” — consistent. No drift. | Keep — validates Principle II. |

**Overflow:** None beyond 10 findings limit.

---

## Coverage Summary Table

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-014/Bad-record isolation | Yes | T004, T007 | JSON parse → problem not exception |
| FR-021/Missing≠Zero | Yes | T006, T012 | git None not 0; SPC null on zero |
| FR-034/Uncertain ledger | Yes | T010 | separate uncertain lane |
| FR-062/063 CLI exit + skipped list | Yes | T015 | `--check` contract |
| NFR-021/022 Escaping/scrub | Yes | T017 | escape_html + scrub_paths |
| SC-005/Coverage print | Yes | T015 Gate1 | 12 weeks correct classification |
| SC-007/Assert gating | Yes | T013/T014 Gate1 | validate returns data |
| Performance <30s/52w | **No** | — | Gap G1 |
| US1 Table before figures | Yes | T009 + Phase2 emit | Canon table printed first (I) |
| US2 Dark-work SPC | Yes | T009 + US2 emit | sessions_per_commit null-or-zero |
| US5 Trust banner | Yes-ish | T018-T023 | Needs explicit [US5] tagging |

**Coverage:** 10/11 buildable requirements have tasks (91%). Ambiguity 1, Duplication 0, Critical 1 (gate, correctly enforced).

---

## Constitution Alignment Issues

- **I CANONICAL FIRST:** Tasks enforce it (Phase 3 gated). Spec/plan language nominally consistent — **no violation** provided CI enforces Gate 1 before chart changes. Fresh v2 must not pre-copy `assets/dashboard.js` without regenerating from canonical table (would violate I).
- **II Missing≠Zero:** Sound. Needs only the timeout→None test addition (C2).
- **IV Per-Item Isolation:** Sound in ingest.
- **VI Legibility:** Spec says hover dims others + adjacent table — weekly emit does this; LD renderer now does lift/chevron for same reason.
- Other principles not violated.

---

## Unmapped Tasks

- `T016 dashboard.css` maps to SC legibility, implicitly US1 — add `[US1]` tag for trace.
- No orphan tasks beyond G1 performance.

---

## Metrics

- Total Requirements (spec FR+SC+US stories): 11 buildable
- Total Tasks (checked): 15 in Phase 1 header sample (full file ~56)
- Coverage: 91%
- Ambiguity: 1
- Duplication: 0
- Critical: 1 (correctly gated, not a defect to fix)

---

## Next Actions

- If CRITICAL gate remains enforced: **proceed** — do not dilute Principle I.
- Optional manual edit: add timeout-None test to T012, clarify 13 vs 36 weeks footnote in spec.md plan.md, add performance timing task or mark NFR.
- Offer remediation: “Would you like concrete patch edits for C2/U1/G1?” — not applied until confirmed.

## Extension Hooks

None (`/.specify/extensions.yml` absent).

## Correlation hooks for this session

- **Page-requirements analysis** (`docs/research/page-requirements-analysis.md`) R1–R3 winners align with spec’s `requirements.md` Purpose “resume from start-here without prior chat” and `what-to-do` queue: micro-header + back-breadcrumb satisfy “compact then progressive disclosure”.
- **Intent archaeology** `derived/prompt-wiki` 535 intents map to pages as in that analysis; no spec page lacks an intent family.
- **Design files** `frontend-design-masterclass` Bento vs Editorial split corresponds to spec’s `Technical Context` performance goals (static, offline, inlined) — taste anti-slop prevents purple/aurora/scale105 regressions that would violate Legibility (VI).

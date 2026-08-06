<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

# Weekly Report Dashboard — governing rules

Read this before writing code. The full constitution is
`.specify/memory/constitution.md`; the parts that change what you do are
reproduced here, because a rule stored in a file nobody opens is not a rule.

Work is defined in `specs/001-weekly-report-dashboard/tasks.md`: 56 tasks,
6 phases, 6 gates. Requirements are in `spec.md`, entities and assertions in
`data-model.md`, contracts in `contracts/`.

## The ordering constraint that may not be relaxed

**Do not begin Phase 3 until Phase 1 is complete and its tests pass.**

Phase 1 builds the canonical data layer. Phase 3 builds the figures.
Constitution Principle I forbids chart code before the canonical table is
assembled, validated, and printed for inspection. Every prior dashboard failure
in this workspace came from drawing charts against ad hoc data, so this is the
one ordering rule that is never relaxed for convenience.

Phase 2 may proceed after Gate 1. Phase 6 tasks may proceed once their
dependencies exist.

## Principles that decide implementation questions

**I. Canonical table first (NON-NEGOTIABLE).** One table. Every chart, count,
label, tooltip, and conclusion derives from it. No figure holds its own copy of
any value. No second hand-maintained list of anything.

**II. Missing is not zero.** A value that was not observed is `null`, never `0`,
never interpolated, never filled from a neighbour. Zero means an observed zero.
Every record carries an explicit `missing_fields` list. `sessions_per_commit` is
`null` when commits is null **or zero** — never infinity. `uncommitted_changes`
is `null` for weeks predating collection, because zero would assert an
observation that never happened.

**III. Provenance on every number.** Source, retrieval timestamp, and a quality
classification of `verified` / `estimated` / `unavailable`. A number without
provenance is not displayed.

**IV. Isolate per-item failure (NON-NEGOTIABLE).** One malformed input must not
abort the rest. A bad record is skipped, counted, and named with a reason.
Silent truncation is prohibited: if coverage is bounded or sampled, say so.

**V. Self-validating output.** The page asserts its own invariants and renders a
visible failure banner when one fails. `--check` exits non-zero so it can gate
automation.

**VI. Legibility is correctness.** Overlapping labels, invisible points, and a
chart stranded in a corner are defects, not cosmetics. Information is never
conveyed by colour alone. Every figure has an adjacent data table.

**VII. Evidence over impression.** No fitted curves, no regression lines, no
interpolation across gaps. Lines connect observed points only; missing weeks are
visible gaps. Where a metric misrepresents reality, say so at the point of
display.

## Hard constraints

- **Offline.** No network request at runtime. The page opens from disk with
  networking disabled and works completely. The chart library is vendored and
  inlined, never fetched.
- **Read-only corpus.** Never write, move, edit, or normalise a weekly report.
  Schema drift is absorbed at ingest, never by mutating historic files.
- **Stdlib only** for the generator, one vendored runtime dependency. Any
  addition needs a recorded reason why existing options are inadequate.
- **No secrets.** Home paths scrubbed to `~`. All corpus text escaped before
  injection into HTML.

## Gates

Do not report a phase complete until its gate passes.

| Gate | Condition |
|---|---|
| 1 | `--check` reports 13 weeks with correct coverage, all assertions pass, exit 0, no corpus file modified |
| 2 | `index.html` opens offline; rebuilds byte-identically |
| 3 | Hovering a series dims the others; no overlapping labels; 2026-08-01 flagged dark-work |
| 4 | Week-over-week trend item shows carry age 4; prose renders escaped and scrubbed |
| 5 | One command regenerates from a clean checkout |
| 6 | A scheduled run regenerates unattended and logs it; curation marks without deleting |

**Permanent regression fixtures.** The 2026-08-01 week (122 sessions,
23 commits, untracked primary deliverable) must be flagged dark-work. The
week-over-week trend carry-over must report carry age 4 — that item is why this
project exists, and shipping it is what closes it.

## Verification

Claims of completion require evidence: `python3 -m pytest tests/ -q` green and
`--check` exit 0. Visual correctness requires **viewing the rendered page as an
image** — passing tests, valid HTML, and DOM inspection are not visual
verification.

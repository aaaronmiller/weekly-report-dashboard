# Weekly Report Dashboard Constitution

## Core Principles

### I. Canonical Table First (NON-NEGOTIABLE)

Build the canonical data table before any figure exists. Every chart, selector,
count, label, tooltip, and conclusion is derived from that one table. Never
maintain a second hand-written list of anything.

No chart code may be written until the table has been assembled, validated, and
printed for inspection. If a value appears in a figure, it MUST be traceable to
a row in the canonical table.

*Origin: user directive, 2026-07-04. Every prior dashboard failure in this
workspace traced to charts drawn against ad hoc data rather than a shared table.*

### II. Missing Is Not Zero

A missing value stays `null` and is labeled. It is never coerced to zero, never
interpolated, never estimated from a neighbor, and never filled from another
series.

Zero means "observed zero". Null means "not observed". Conflating them is a
correctness defect, not a display preference. Every record carries an explicit
`missing_fields` list, and the count of missing data is displayed to the user
rather than hidden.

### III. Provenance On Every Number

Every metric carries its source, retrieval timestamp, and a quality
classification of `verified`, `estimated`, or `unavailable`.

A number without provenance may not be displayed. When a value comes from a
fallback path rather than its primary source, the fallback is named at the point
of display, not buried in a footnote.

### IV. Isolate Per-Item Failure (NON-NEGOTIABLE)

One malformed input MUST NOT abort processing of the rest. A bad record is
skipped, counted, and reported by name with a reason.

*Origin: on 2026-08-01 a single unknown reference aborted an entire corpus sync
and left twenty finished pages unpublished with no visible error. The failure was
not the bad record; it was that one bad record could silence everything else.*

Silent truncation is prohibited. When coverage is bounded, dropped, or sampled,
the generator states what was dropped and why. A run that quietly covers less
than it appears to is worse than a run that fails loudly.

### V. Self-Validating Output

The generated artifact asserts its own invariants and displays a visible failure
banner when an assertion does not hold. The generator exits non-zero on any
failed assertion so it can gate automation.

An artifact that looks correct while being wrong is the specific failure this
project exists to prevent. Assertions are emitted as data alongside the results,
so the page can report its own health without a running service.

### VI. Legibility Is Correctness

An unreadable figure is a broken figure. Overlapping labels, invisible points,
charts stranded in a corner, and whitespace dominated by one outlier are defects,
not cosmetic issues.

Information is never conveyed by color alone. Every figure has an adjacent data
table carrying the same values. Hovering a point brings its series into focus so
overlapping data stays inspectable.

*Origin: recorded user feedback, 2026-07-03: the graphs were "hard as fuck to
read", had no visible population under the line, and omitted valid points.*

### VII. Evidence Over Impression

The dashboard reports observed history. It does not forecast, smooth, fit
curves, draw regression lines, or interpolate across gaps. Lines connect observed
points only; missing weeks render as visible gaps.

Where a metric is known to misrepresent reality, the dashboard says so at the
point of display. Commit counts that understate a week of uncommitted work MUST
be flagged as understating it.

## Additional Constraints

**Offline and self-contained.** The artifact makes no network request at
runtime. It opens from disk with networking disabled and functions completely.
All data, styles, scripts, and chart libraries are embedded.

**Read-only with respect to evidence.** The weekly report corpus is input. The
generator never writes, moves, edits, or normalizes a report. Schema drift is
absorbed at ingest, never by mutating historic files.

**No second task database.** Living Documents remains the authority for tasks,
decisions, and blockers. This dashboard is a projection of durable evidence, not
a competing source of truth.

**Dependency minimalism.** The generator uses the Python standard library. The
runtime has exactly one vendored dependency, version-pinned and never fetched at
runtime. Any additional dependency requires a recorded reason why existing
options are inadequate.

**No secrets in output.** Home paths are scrubbed. Credentials, tokens, and
provider keys are never read or emitted. All corpus text is escaped before
injection into HTML.

## Quality Gates

1. **Data layer before presentation.** Ingestion, canonicalization, and
   validation pass their tests against the real corpus before any chart exists.
2. **Idempotence.** Two runs over unchanged input produce byte-identical output.
3. **Offline check.** Verified by opening the artifact with networking disabled.
4. **Visual verification.** Rendered output is inspected as an image. DOM
   presence, passing tests, and HTML inspection are not visual verification.
5. **Assertion gate.** `--check` exits non-zero on any failed invariant.
6. **Known-week fixture.** The 2026-08-01 week, with 122 sessions and 23 commits
   against an untracked primary deliverable, is a permanent regression fixture.
   A dashboard that fails to flag it has regressed.

## Governance

This constitution supersedes other practices for this project. Where a
requirement and a principle conflict, the principle governs and the requirement
is amended.

Amendments require a recorded rationale and a version increment. Principles
marked NON-NEGOTIABLE may not be relaxed to make an implementation easier; the
implementation changes instead.

Complexity must be justified against the stated scope. Any proposal to add a
runtime service, a build toolchain, a second data source, or a dependency must
state why the existing approach is inadequate.

**Version**: 1.0.0 | **Ratified**: 2026-08-01 | **Last Amended**: 2026-08-01

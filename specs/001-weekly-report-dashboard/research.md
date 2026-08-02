# Research: Weekly Report Dashboard

## R-1: Charting library

**Decision**: Apache ECharts 5.x, vendored and inlined.

**Question**: Which library satisfies the two hardest visualization requirements
natively — hover-focuses-a-series-and-dims-others (FR-041) and
labels-must-never-overlap (FR-042)?

**Evidence**: A 2026 survey of JavaScript charting libraries places Chart.js as
the most widely used (~10M weekly downloads) with the simplest API, ECharts as
the strongest for large datasets and complex dashboards, D3 as maximally
flexible with the steepest cost, and Recharts as React-specific with SVG
performance limits.

ECharts 5.0 introduced a unified `emphasis` / `blur` / `select` state model with
`focus` and `blurScope` options, which is exactly the series-focus behavior
FR-041 describes. Its `labelLayout` provides `hideOverlap` as a built-in
collision resolver, which is FR-042.

**Alternatives rejected**:

| Option | Why rejected |
| --- | --- |
| Chart.js | No series-blur concept; series focus requires manual color mutation on every hover event. Label collision needs a third-party plugin, adding a second dependency. |
| Plotly | Satisfies the features but its bundle is substantially larger, and page weight is capped at 3 MB by NFR-003 with ~1 MB already going to the library. |
| D3 | Unlimited flexibility, but axes, legends, tooltips, and collision detection are all hand-written. Unjustified for four fixed chart types. |
| Recharts | React-specific; this project has no React and each data point maps to an SVG element, which degrades at the point counts involved. |

**Corroborating user evidence**: The recorded complaint of 2026-07-03 — graphs
"hard as fuck to read", missing population under the line, overlapping labels —
describes precisely the failure modes that `hideOverlap` and `emphasis.focus`
exist to prevent. Choosing a library where these are native rather than bolted on
is a direct response to that feedback.

**Sources**:
- https://www.pkgpulse.com/guides/best-javascript-charting-libraries-2026
- https://embeddable.com/blog/javascript-charting-libraries
- https://echarts.apache.org/en/changelog.html
- https://apache.github.io/echarts-handbook/en/concepts/style/

---

## R-2: Vendored library versus CDN

**Decision**: Vendor a pinned minified build; inline it at emit time.

**Rationale**: NFR-020 forbids runtime network access and AS-7 requires the page
to function with networking disabled. A CDN reference fails both. Vendoring also
pins the version so builds stay reproducible (SC-005) and removes a supply-chain
fetch path.

**Cost accepted**: ~1 MB of the 3 MB budget. This is the dominant page-weight
line item and the single largest tradeoff in the design.

---

## R-3: Static artifact versus Grafana

**Decision**: Static self-contained HTML. Grafana and Prometheus remain for live
operational metrics and are not replaced.

**Rationale**: The user confirmed the Grafana/Prometheus pairing on 2026-05-19
("yes grafana was it - and prometheus is also correct"), and
`prometheus_exporter.py` plus Grafana provisioning already exist in the suite.
They are correct for live metrics.

They are wrong for this artifact. Grafana requires a running server and a live
datasource; this must open from disk, work offline, and stay readable years
later as a historical record. The two are complementary: Prometheus owns live
state, this owns narrative history.

---

## R-4: Markdown rendering

**Decision**: A restricted in-house renderer over the subset the corpus uses.

**Rationale**: The reports use headings, paragraphs, tables, checkboxes, bold,
and code spans. A full CommonMark implementation is a dependency and a much
larger surface than needed. A restricted renderer that escapes all input first
(NFR-021) is roughly 80 lines and safer by construction, since it cannot be
induced to emit HTML present in the source.

**Risk**: A future report using an unsupported construct degrades to literal
text. Acceptable and visible, rather than silently mis-rendered.

---

## R-5: Carry-over text matching

**Decision**: Conservative normalization; unmatched items stay separate and are
labeled `uncertain`.

**Question**: How are the same commitments matched across weeks when their
annotations change?

**Observed pattern**: The same item appears as
`- [ ] Week-over-week trend comparison` in one week and
`- [ ] Week-over-week trend comparison (carry-over from Jul 11, Jul 19)` in
another. The trailing parenthetical varies while the commitment does not.

**Approach**: Lowercase, strip trailing parentheticals, collapse whitespace,
strip punctuation. Exact match wins; normalized match is accepted and labeled;
anything weaker stays a separate item marked `uncertain`.

**Why conservative**: A false merge understates carry age, and carry age is the
metric the feature exists to produce. A false split is visible in the ledger and
correctable; a false merge is invisible and corrupts the headline number. The
failure mode is deliberately chosen to be the visible one.

**Rejected**: Fuzzy or embedding-based similarity. Both introduce a threshold
that silently merges near-misses, which is the failure mode being avoided, and
embeddings would add a model dependency to a stdlib-only generator.

---

## R-6: Uncommitted-work measurement

**Decision**: Record `git status --porcelain` counts per project at collection
time. Historic weeks are `unavailable`, never zero.

**Rationale**: The 2026-08-01 week recorded 23 commits while nine modules and
seven test files sat untracked. Commit count alone reported the week as ordinary.
Sessions-per-commit (122 / 23 ≈ 5.3) plus an uncommitted-file count exposes it.

**Limitation, stated rather than worked around**: Uncommitted state at a past
moment is not reconstructible from git history. Backfilling is impossible, so
prior weeks are labeled `unavailable` under Principle II rather than given a
zero that would falsely assert "we looked and found nothing".

---

## R-7: Idempotence mechanism

**Decision**: Sorted keys, fixed JSON separators, and no timestamp in the
content-bearing payload.

**Problem**: `generated_at` changes every run, which would break byte-identical
output (SC-005).

**Approach**: Place `generated_at` in a designated header region excluded from
the idempotence comparison, or derive it from the newest input file's mtime so
it is a function of inputs. The second is preferred: it keeps the whole file
byte-stable and makes the timestamp meaningful, since it then reports the
evidence date rather than the build date.

---

## R-8: Corpus location

**Decision**: Read reports from `/home/cheta/code/weekly-reports/` and bundles
from `/home/cheta/code/weekly-report-dashboard/`, reconciling by week-ending
date.

**Finding**: The corpus is split. Thirteen report pairs live in
`weekly-reports/`, while the `2026-07-05` pair sits in `/home/cheta/code/`
instead. Six bundles live in `weekly-report-dashboard/`. Reconciliation is
required regardless, and coverage classification (`pair-only`, `bundle-only`)
makes the split visible rather than hiding it.

**Note**: Consolidating the stray pair is recorded as a corpus-hygiene item, not
a code change. The generator must handle the split either way, since it will
recur.

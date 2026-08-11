# Improvement notes -- week ending 2026-08-07

## Evidence gathering

- Easy: git logs, dashboard state (pytest, --check, crontab), raw-mirror counts, LD history gates.
- Hard: session counts. CASS index stale since 08-06; collector reported 9 sessions while raw-mirror holds 31. The canonical collector should read raw-mirror manifests (the dashboard's own primary source) rather than the cass timeline alone.
- Missing: token/cost telemetry for the week (M5/M6 stubs); heatmap real-daily backfill.

## Metrics issues

- Kanban `done` items stale for the second week (dated 07-05..07-08); `work_done/wip/planned` and momentum score are artifacts. Excluded from narrative.
- Files-changed (1,002) inflated by `backup:` and corpus commits (living-documents backup 307 files, model-scan classifier corpus). Classify backup commits separately in the collector.

## Categories / visualizations to add

- A "published vs uncommitted" lane: this week's headline was closing an untracked-risk; the dashboard should track `git status --porcelain` per project per week (recommended Aug 1, still not built).
- Sessions-per-commit trend (recommended Aug 1, still not built; this week's density on 08-05 makes it visible).
- Week-over-week trend comparison: carry age 5. The D-group charts partially cover it; decide build or drop.

## Dad report

- ~610 words, within target; career + mentor sections just over one-third per request.
- The archaeology-to-shipped arc worked as the theme and was verifiable end to end.
- Next week: keep the mentor list visible in the Next Milestone section so follow-through is checkable week over week.

## Personal report

- Preserved dates, commit hashes, and gate evidence for future dashboard backfill.
- Marked the momentum score as a collector artifact in Metrics, not the narrative.

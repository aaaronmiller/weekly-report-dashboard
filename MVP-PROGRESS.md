---
title: MVP dashboard progress
date: 2026-11-17
---

# MVP dashboard progress

## R19, R20 and R21 capacity and pace

Attempted. The dashboard now has an offline dsctl capacity section with pool
windows, pace, informational mode, freshness, efficiency availability,
concurrency proxies, and meta-analysis history. The capacity renderer accepts
an explicit export and only emits selected fields. Raw notes and command
arguments are not included. Session and agent counts remain unavailable
because the telemetry contract does not supply them.

Evidence:

- Offline `dsctl-telemetry export --out /tmp/dashboard-telemetry.json`: exit 0.
- `python3 -m pytest tests/test_capacity.py tests/test_emit.py -q`: 4 passed.
- `python3 scripts/build_dashboard.py --check`: exit 0; all assertions passed.
- `python3 scripts/build_dashboard.py --capacity-telemetry /tmp/dashboard-telemetry.json --out /tmp/dashboard-build`: exit 0 and section present.
- Whole-page `grep` of the temporary live build found home paths and the local
  username. The hostname was absent. The existing dashboard payload includes
  private content from multiple unrelated inputs. The prior tracked page also
  contains home paths and the username. A clean public page therefore cannot
  be asserted from the capacity allowlist alone.
- `git diff --check`: passed.
- `python3 -m pytest tests/ -q`: 29 passed, 1 failed in 199.67 seconds.
  `tests/test_integration.py::test_idempotence` found different bytes between
  consecutive builds. The reported offset falls in the existing
  `projects_stats.months[].files` payload; the reason for the difference has
  not been established. The integration test restored its temporary mutation
  of the tracked metrics fixture.

The live build was kept in a temporary directory instead of replacing the
tracked page. Whole-page public sanitization, including exclusion of prompts
and argument content, and visual browser verification remain open. The
full suite must also pass before the section can be called complete.

## Next task

Finish the public-output privacy boundary and verify the live-generated page,
then address T-01 in the dashboard dossier if its owner-triage requirement can
be fulfilled with the dossier held read-only. No commit or push was made under
the Codex sandbox instruction.

## Privacy scrub, 2026-11-17

Implemented the named scrub locally. `scripts/emit.py` applies one final output
sanitizer to both generated HTML files. It replaces Unix home prefixes with
`~` and redacts the local account name, home-directory name, hostname and
fully qualified hostname, case-insensitively. JSON is emitted as Unicode so the
same boundary covers non-ASCII identities. Relative paths are preserved.

Feed audit: `build_dashboard.py` passes canonical reports, bundles, Git state,
primary session data, project, Claude, system, browser, Obsidian, harness,
subscription, Git, Tokscale and capacity stats, plus telemetry, Living
Documents task data and the LLM supplement to `emit.py`. The renderer also
reads report prose and settings and inlines assets. Any text from these sources
can reach a page, so sanitization is applied to the complete generated pages.
The capacity renderer additionally allowlists its own fields. The scrub does
not identify all personal information or historic identities from other hosts.

Evidence:

- `python3 -m pytest tests/test_emit.py tests/test_capacity.py -q`: 5 passed,
  including fixture data across optional feeds, report prose, JSON keys and
  settings, plus preserved repo-relative paths and parsed output JSON.
- `/home/cheta/code/dsctl/bin/dsctl-telemetry export --out /tmp/weekly-dashboard-privacy-telemetry.json`: exit 0.
- `python3 scripts/build_dashboard.py --capacity-telemetry /tmp/weekly-dashboard-privacy-telemetry.json`: exit 0, 57 weeks, all assertions passed; regenerated `index.html`.
- `python3 scripts/build_dashboard.py --check`: exit 0, 57 weeks, all assertions passed.
- Case-insensitive fixed-string `grep` on `index.html` and `settings.html`
  found no `/home/`, local username, short hostname or fully qualified hostname.
- All five inline scripts passed `node --check`; all three inline JSON payloads
  parsed. `git diff --check` passed.
- Full suite `python3 -m pytest tests/ -q`: 29 passed, 1 failed in 184.78s.
  This run began before the new fixture test was added; that fixture passed in
  the focused run above. The idempotence test's first build could not open the
  CASS database and used a different source; its second build opened CASS.
  Session totals changed from 8812 to 7336, so identical inputs were not
  observed. This is a real test-environment availability change, not evidence
  that identical inputs yielded different output. The prior reported
  `projects_stats.months[].files` difference could not be reproduced: two
  successive `build_projects_stats` scans returned identical monthly totals.
  `_git_stats` catches timeouts and can silently return partial results, a
  plausible source of variation that was not independently demonstrated here.
  The existing idempotence gate remains failing and has not been weakened.

Next task attempted: T-01 requires owner triage to be recorded in the dossier's
`tasks.md`. That file is explicitly read-only for this worker, and the task
requires an owner decision. `intent-find` returned no matching derived intents.
Best next action is for the owner to authorize a dossier writer and decide or
record dispositions for the three asks. No commit was made because the current
request prohibits it. No push was made: origin is a GitHub URL, not the private
bare local repository described in the instruction.

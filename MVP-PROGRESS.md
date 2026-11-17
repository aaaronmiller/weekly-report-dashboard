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

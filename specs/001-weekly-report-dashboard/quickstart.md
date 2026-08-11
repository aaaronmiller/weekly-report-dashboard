# Quickstart: Weekly Report Dashboard

## Build

```bash
cd /home/cheta/code/weekly-report-dashboard
python3 scripts/build_dashboard.py
```

Defaults read reports from `/home/cheta/code/weekly-reports`, bundles from this
directory, and write `index.html` here.

## Validate without writing

```bash
python3 scripts/build_dashboard.py --check
echo $?    # 0 = all assertions passed, 1 = one or more failed
```

## Run the tests

```bash
python3 -m pytest tests/ -q
```

## Verify the result

Four checks, in order of what they catch:

**1. Offline function.** Disable networking, then open `index.html` from disk.
Every figure, tooltip, legend toggle, and week selector must work. This is the
single most important check: a page that silently depends on a CDN passes every
other test and fails in the only condition that matters.

**2. Idempotence.**

```bash
python3 scripts/build_dashboard.py && sha256sum index.html > /tmp/a
python3 scripts/build_dashboard.py && sha256sum index.html > /tmp/b
diff /tmp/a /tmp/b && echo "idempotent"
```

**3. Failure isolation.** Corrupt one bundle and rebuild:

```bash
cp 2026-07-11/weekly-metrics.json /tmp/bundle.bak
echo '{ broken' > 2026-07-11/weekly-metrics.json
python3 scripts/build_dashboard.py
# expect: run completes, 2026-07-11 named as skipped with a reason,
#         remaining 12 weeks still render
cp /tmp/bundle.bak 2026-07-11/weekly-metrics.json
```

**4. Visual inspection.** Open the page and look at it. Confirm no overlapping
labels, no chart stranded in a corner, no invisible points, and that hovering a
series dims the others.

Per the standing rule, this must be done by viewing the rendered page as an
image. Passing tests, valid HTML, and DOM presence are not visual verification.

## Expected output on the current corpus

| Check | Expected |
| --- | --- |
| Weeks discovered | 12 |
| Weeks with a metrics bundle | 6 |
| Weeks with a report pair | 12 |
| 2026-08-01 dark-work flag | set (122 sessions, 23 commits) |
| Week-over-week trend carry age | 4 |
| Assertions | all pass |
| Page weight | under 3 MB |

If the trend item does not show carry age 4, carry-over matching is wrong. That
item is the project's own regression fixture: it is the reason the dashboard
exists, and shipping this feature is what closes it.

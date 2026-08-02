# Contract: Command-Line Interface

## Command

```bash
python3 scripts/build_dashboard.py \
  --reports  <dir>   # default /home/cheta/code/weekly-reports
  --bundles  <dir>   # default /home/cheta/code/weekly-report-dashboard
  --out      <dir>   # default same as --bundles
  [--weeks N]                    # display window; default all
  [--dark-work-threshold FLOAT]  # sessions per commit; default 8.0
  [--stall-age INT]              # carry age marking stalled; default 3
  [--check]                      # validate only; write nothing
```

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Success; all assertions passed |
| 1 | One or more assertions failed |
| 2 | No input discovered at the given paths |

Exit 1 with `--check` is the gating mode: it validates the corpus without
writing, so it can run in a pre-commit hook.

## Stdout contract

Human-readable summary. Must always state:

- weeks discovered, and their coverage classification counts
- every week skipped, named, with the reason
- every failed assertion, named
- output path and byte size on success

Silent truncation is prohibited (FR-063). If the run bounded, sampled, or
dropped anything, it says so on stdout.

## Side effects

Writes exactly one file: `<out>/index.html`.

Reads, and never writes, the report corpus and metrics bundles. Executes
`git status --porcelain` read-only against discovered project directories.

## Idempotence

Two consecutive runs over unchanged inputs must produce byte-identical output
(SC-005). `generated_at` derives from the newest input file's mtime, not from
wall-clock time, so the timestamp is a function of the inputs.

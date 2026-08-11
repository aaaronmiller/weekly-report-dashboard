from scripts.ingest import discover_reports, discover_bundles
from scripts.canonicalize import build_week_records, build_carry_over_ledger, build_project_activity
from scripts.validate import validate_canonical

def test_each_assertion_passes_on_real_corpus():
    reports, _ = discover_reports("/home/cheta/code/weekly-reports")
    bundles, _ = discover_bundles("/home/cheta/code/weekly-report-dashboard")
    weeks = build_week_records(reports, bundles)
    carry = build_carry_over_ledger(reports)
    proj = build_project_activity(bundles)
    assertions = validate_canonical(weeks, carry, proj)
    for a in assertions:
        assert a.passed, f"{a.assertion_id} failed: {a.description}"

def test_each_fails_when_precondition_broken():
    reports, _ = discover_reports("/home/cheta/code/weekly-reports")
    bundles, _ = discover_bundles("/home/cheta/code/weekly-report-dashboard")
    weeks = build_week_records(reports, bundles)
    carry = build_carry_over_ledger(reports)
    proj = build_project_activity(bundles)
    # break A-003: set sessions_per_commit non-null when commits zero
    if weeks:
        w = weeks[0]
        orig = w.sessions_per_commit
        w.commits = 0
        w.sessions_per_commit = 5.0
        assertions = validate_canonical(weeks, carry, proj)
        a003 = [a for a in assertions if a.assertion_id == "A-003"][0]
        assert not a003.passed
        w.sessions_per_commit = orig
        w.commits = 5

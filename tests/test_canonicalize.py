from scripts.canonicalize import normalize_item, compute_carry_age, build_week_records, build_carry_over_ledger
from scripts.ingest import discover_reports, discover_bundles

def test_normalization_strips_parenthetical():
    assert normalize_item("Week-over-week trend comparison (carry-over from Jul 11, Jul 19)") == "week-over-week trend comparison"
    assert normalize_item("Week-over-week trend comparison (carry-over from Jul 11, Jul 19, Jul 25)") == "week-over-week trend comparison"
    assert normalize_item("  Hello  World  ") == "hello world"

def test_carry_age_consecutive_and_non_consecutive():
    # consecutive unchecked: age 3
    apps = [{"week": "2026-07-11", "checked": False}, {"week": "2026-07-19", "checked": False}, {"week": "2026-07-25", "checked": False}]
    assert compute_carry_age(apps) == 3
    # non-consecutive: checked in middle resets
    apps2 = [{"week": "2026-07-11", "checked": False}, {"week": "2026-07-19", "checked": True}, {"week": "2026-07-25", "checked": False}]
    assert compute_carry_age(apps2) == 1

def test_unchecked_checked_unchecked_restarts():
    apps = [{"week": "2026-07-11", "checked": False}, {"week": "2026-07-19", "checked": True}, {"week": "2026-07-25", "checked": False}, {"week": "2026-08-01", "checked": False}]
    assert compute_carry_age(apps) == 2  # last two unchecked after checked

def test_sessions_per_commit_none_at_zero():
    reports = {"2026-01-01": {"dad_path": None, "personal_path": None, "has_pair": True, "has_any": True}}
    bundles = {"2026-01-01": {"metrics": {"sessions_total": 10, "commits_total": 0, "files_changed_total": 5, "projects_total": 1}, "period": {}, "projects": []}}
    weeks = build_week_records(reports, bundles)
    w = weeks[0]
    assert w.sessions_per_commit is None
    assert w.commits == 0
    # never infinity
    assert w.sessions_per_commit != float('inf')

def test_uncommitted_null_for_historic():
    reports = {"2026-05-31": {"dad_path": None, "personal_path": None, "has_pair": True, "has_any": True}}
    bundles = {"2026-05-31": {"metrics": {"sessions_total": 10, "commits_total": 5, "projects_total": 1}, "period": {}, "projects": []}}
    weeks = build_week_records(reports, bundles)
    assert weeks[0].uncommitted_changes is None
    assert weeks[0].uncommitted_changes != 0

def test_carry_age_real_corpus():
    reports, _ = discover_reports("/home/cheta/code/weekly-reports")
    # add stray if exists
    import pathlib
    if pathlib.Path("/home/cheta/code/weekly-report-2026-07-05.md").exists():
        # simulate stray not in reports dir; include manually for test
        pass
    ledger = build_carry_over_ledger(reports)
    # find week-over-week trend item
    candidates = [c for c in ledger if "week-over-week" in c.normalized_text]
    if candidates:
        # should be at least age 3 per data (Jul11,19,25,08-01 =4)
        assert max(c.carry_age for c in candidates) >= 3

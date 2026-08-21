import pathlib, json, tempfile, shutil, subprocess

# Every build subprocess is bounded. Without this a slow or hung build blocks
# the whole suite indefinitely: on 2026-08-20 the build took 36.5s and
# test_idempotence runs it twice, so the suite looked like a hang rather than
# a slow test. The bound is deliberately well above the ~11s a healthy build
# now takes, so it catches a hang without failing on ordinary variance.
BUILD_TIMEOUT = 120
from scripts.ingest import discover_reports, discover_bundles

def test_idempotence(tmp_path):
    # run build twice and compare
    out = pathlib.Path("/tmp/test_idem_out")
    out.mkdir(exist_ok=True)
    subprocess.run(["python3", "scripts/build_dashboard.py", "--out", str(out)],
                   check=True, timeout=BUILD_TIMEOUT)
    a = (out / "index.html").read_bytes()
    subprocess.run(["python3", "scripts/build_dashboard.py", "--out", str(out)],
                   check=True, timeout=BUILD_TIMEOUT)
    b = (out / "index.html").read_bytes()
    assert a == b

def test_malformed_bundle(tmp_path):
    # inject corrupt bundle
    bundles_dir = pathlib.Path("/home/cheta/code/weekly-report-dashboard")
    target = bundles_dir / "2026-07-11" / "weekly-metrics.json"
    backup = tmp_path / "bak.json"
    original = target.read_bytes()

    # Refuse to run against an already-corrupt source. This test mutates a real
    # tracked corpus file and restores it in `finally`. On 2026-08-20 the
    # corrupted content was found committed at HEAD, which means a run once
    # died between the write and the restore, the damage was committed, and
    # every later run then "backed up" the corruption and faithfully restored
    # it. Validating first turns that silent, self-perpetuating data loss into
    # an immediate failure.
    import json as _json
    try:
        _json.loads(original)
    except Exception as exc:
        raise AssertionError(
            f"{target} is already corrupt and must be repaired before this test "
            f"runs, otherwise the corruption gets preserved: {exc}")
    backup.write_bytes(original)
    try:
        target.write_text("{ broken")
        result = subprocess.run(["python3", "scripts/build_dashboard.py", "--check"],
                                capture_output=True, text=True, timeout=BUILD_TIMEOUT)
        assert result.returncode in (0,1)  # should not crash
        assert "2026-07-11" in result.stdout or "skipped" in result.stdout.lower()
        # remaining weeks still render: run full build to temp out
        out = tmp_path / "out"
        out.mkdir()
        result2 = subprocess.run(["python3", "scripts/build_dashboard.py", "--out", str(out)],
                                 capture_output=True, text=True, timeout=BUILD_TIMEOUT)
        assert result2.returncode in (0,1)
        assert (out / "index.html").exists()
        # check that file contains weeks
        html = (out / "index.html").read_text()
        assert "week" in html.lower()
    finally:
        target.write_bytes(backup.read_bytes())

def test_dark_work_fixture():
    reports, _ = discover_reports("/home/cheta/code/weekly-reports")
    bundles, _ = discover_bundles("/home/cheta/code/weekly-report-dashboard")
    from scripts.canonicalize import build_week_records
    weeks = build_week_records(reports, bundles)
    w = [x for x in weeks if x.week_ending.isoformat() == "2026-08-01"]
    assert w, "2026-08-01 not found"
    w = w[0]
    assert w.sessions == 122
    assert w.commits == 23
    assert w.is_dark_work is True

def test_carry_age_fixture():
    reports, _ = discover_reports("/home/cheta/code/weekly-reports")
    from scripts.canonicalize import build_carry_over_ledger
    ledger = build_carry_over_ledger(reports)
    # week-over-week trend item
    candidates = [c for c in ledger if "week-over-week trend" in c.normalized_text]
    assert candidates, "trend item not found"
    max_age = max(c.carry_age for c in candidates)
    # Consecutive unchecked streak 2026-07-11..2026-08-07 = 5 appearances.
    # Was 4 through 2026-08-01; advanced to 5 when the 08-07 week landed.
    # The 08-07 report itself records "carry age 5 -- decide build or drop".
    assert max_age == 5, f"expected carry age 5, got {max_age}"

import pathlib, json, tempfile
from scripts.ingest import discover_reports, discover_bundles, parse_carry_over
from scripts.canonicalize import normalize_item, build_week_records, build_carry_over_ledger

def test_report_pairing(synthetic_corpus):
    reports, probs = discover_reports(synthetic_corpus["reports"])
    assert "2026-01-03" in reports
    assert reports["2026-01-03"]["has_pair"] is True
    assert "2026-01-10" in reports
    assert reports["2026-01-10"]["has_pair"] is True

def test_bundle_schema_drift(tmp_path):
    d = tmp_path / "2026-01-01"
    d.mkdir()
    # minimal valid bundle
    (d / "weekly-metrics.json").write_text(json.dumps({"metrics": {"sessions_total": 5, "commits_total": 2}}))
    bundles, probs = discover_bundles(tmp_path)
    assert "2026-01-01" in bundles
    # corrupt bundle
    d2 = tmp_path / "2026-01-08"
    d2.mkdir()
    (d2 / "weekly-metrics.json").write_text("{ broken")
    bundles2, probs2 = discover_bundles(tmp_path)
    assert any("parse error" in p["reason"].lower() or "json" in p["reason"].lower() for p in probs2)
    # should not raise

def test_checkbox_parsing(tmp_path):
    p = tmp_path / "personal.md"
    p.write_text("## Project Pipeline with Carry-Over\n\n### Proj\n- [ ] todo\n- [x] done\n- [X] Done caps\n")
    items, note = parse_carry_over(p)
    assert len(items) == 3
    assert items[0]["checked"] is False
    assert items[1]["checked"] is True

def test_missing_carry_over_section(tmp_path):
    p = tmp_path / "personal.md"
    p.write_text("# No section\n- [ ] ignore")
    items, note = parse_carry_over(p)
    assert items == []
    assert note is not None

def test_corrupt_bundle_produces_problem_not_exception(synthetic_corpus):
    # synthetic already has corrupt handling via discover_bundles
    bdir = synthetic_corpus["bundles"] / "2026-01-20"
    bdir.mkdir()
    (bdir / "weekly-metrics.json").write_text("{ not json")
    bundles, probs = discover_bundles(synthetic_corpus["bundles"])
    assert any("2026-01-20" in p["path"] for p in probs)
    # should still have other bundles
    assert "2026-01-03" in bundles

def test_malformed_filename(tmp_path):
    (tmp_path / "weekly-report-bad.md").write_text("x")
    (tmp_path / "weekly-report-2026-13-40.md").write_text("x")  # invalid date
    reports, probs = discover_reports(tmp_path)
    assert len(probs) >= 1
    # should not raise

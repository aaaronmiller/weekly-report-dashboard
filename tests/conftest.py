import pathlib
import json
import tempfile
import shutil

import pytest


@pytest.fixture
def real_reports_dir():
    return pathlib.Path("/home/cheta/code/weekly-reports")

@pytest.fixture
def real_bundles_dir():
    return pathlib.Path("/home/cheta/code/weekly-report-dashboard")

@pytest.fixture
def synthetic_corpus(tmp_path):
    """Build a synthetic 3-week corpus for isolated tests."""
    reports = tmp_path / "reports"
    bundles = tmp_path / "bundles"
    reports.mkdir()
    bundles.mkdir()
    # week 1: pair with bundle
    (reports / "weekly-report-2026-01-03.md").write_text("# Week 1\n\n## Project Pipeline with Carry-Over\n\n### ProjA\n- [ ] Do thing\n")
    (reports / "weekly-report-2026-01-03-personal.md").write_text("# Week 1 personal\n\n## Project Pipeline with Carry-Over\n\n### ProjA\n- [ ] Do thing\n")
    d1 = bundles / "2026-01-03"
    d1.mkdir()
    (d1 / "weekly-metrics.json").write_text(json.dumps({
        "period": {"start": "2025-12-28", "end": "2026-01-03"},
        "generated_at": "2026-01-03T00:00:00+00:00",
        "metrics": {"sessions_total": 10, "commits_total": 5, "files_changed_total": 20, "projects_total": 2, "momentum_score": 50},
        "projects": [{"name": "proj", "commits": 5, "files_changed": 20, "state": "active"}],
        "daily_activity": [{"date": "2026-01-01", "sessions": 2}]
    }))
    # week 2: pair only
    (reports / "weekly-report-2026-01-10.md").write_text("# Week 2\n")
    (reports / "weekly-report-2026-01-10-personal.md").write_text("# Week 2 personal\n\n## Project Pipeline with Carry-Over\n\n### ProjA\n- [ ] Do thing\n- [x] Done thing\n")
    # week 3: bundle only (no reports)
    d3 = bundles / "2026-01-17"
    d3.mkdir()
    (d3 / "weekly-metrics.json").write_text(json.dumps({
        "period": {"start": "2026-01-11", "end": "2026-01-17"},
        "generated_at": "2026-01-17T00:00:00+00:00",
        "metrics": {"sessions_total": 15, "commits_total": 0, "files_changed_total": 30, "projects_total": 1, "momentum_score": 60},
        "projects": [],
        "daily_activity": []
    }))
    return {"reports": reports, "bundles": bundles}

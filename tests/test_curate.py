import pathlib
from scripts.curate import classify_passages, curate_file

def test_process_asides_marked_not_removed(tmp_path):
    text = "Process meta discussion about workflow.\n\nNormal content about feature.\n\nJob search reference: applied to 5 jobs."
    classified = classify_passages(text)
    # process should be marked but not removed
    assert any(c["label"] == "process" for c in classified)
    assert len(classified) == 3

def test_job_search_survives(tmp_path):
    text = "Job search: 5 applications submitted.\n\nProcess aside."
    classified = classify_passages(text)
    job = [c for c in classified if "job" in c["passage"].lower()]
    assert job[0]["label"] == "keep"
    assert job[0]["rule"] == "job_search_retention"

def test_summary_count_matches(tmp_path):
    p = tmp_path / "sample.md"
    p.write_text("Job search paragraph.\n\nProcess meta paragraph.\n\nKeep paragraph.")
    result = curate_file(p)
    total = result["summary"]["total"]
    assert total == 3
    assert sum(result["summary"]["by_label"].values()) == total

def test_source_unchanged(tmp_path):
    p = tmp_path / "sample2.md"
    content = "Job search.\n\nProcess."
    p.write_text(content)
    before = p.read_bytes()
    curate_file(p)
    after = p.read_bytes()
    assert before == after

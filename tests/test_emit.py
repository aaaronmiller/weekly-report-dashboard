from scripts.emit import escape_html, scrub_paths, serialize_payload
from datetime import datetime, timezone, date
from scripts.models import WeekRecord, CarryOverItem, ProjectWeekActivity, ValidationAssertion
import json

def test_escaping():
    assert escape_html("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert "&" in escape_html("a & b")

def test_path_scrubbing():
    assert scrub_paths("/home/cheta/code/file") == "~/code/file"
    assert scrub_paths("/home/other/path") == "~/path"
    assert scrub_paths("no path") == "no path"

def test_payload_sorts_keys_and_nulls():
    w = WeekRecord(week_ending=date(2026,8,1), has_pair=True, has_bundle=True, coverage="pair+bundle", sessions=None, commits=None, missing_fields=["sessions"], data_quality="unavailable")
    a = ValidationAssertion(assertion_id="A-001", description="x", expected=True, actual=True, passed=True)
    payload = serialize_payload(([w], [], []), [a], {"dark_work_threshold": 8.0, "stall_age": 3}, datetime(2026,8,1, tzinfo=timezone.utc))
    data = json.loads(payload)
    # nulls serialize as null not 0
    assert data["weeks"][0]["sessions"] is None
    # sort_keys
    assert payload.index('"coverage"') < payload.index('"weeks"')
    # null not 0
    assert "null" in payload


def test_build_scrubs_all_emitted_sources(tmp_path, monkeypatch):
    from scripts import emit

    monkeypatch.setattr(emit.getpass, "getuser", lambda: "fixtureuser")
    monkeypatch.setattr(emit.socket, "gethostname", lambda: "fixturehost")
    monkeypatch.setattr(emit.socket, "getfqdn", lambda: "fixturehost.example")
    private = "/home/fixtureuser/code/project fixtureuser fixturehost.example fixturehost"
    report = tmp_path / "report.md"
    report.write_text(private + " relative/src.py", encoding="utf-8")
    week = WeekRecord(week_ending=date(2026, 8, 1), dad_report_path=str(report),
                      coverage="fixture", data_quality="verified")
    feed = {private: [private, "relative/src.py"]}
    names = ("llm_supplement", "subscription_value", "harness_stats", "projects_stats",
             "obsidian_stats", "browser_stats", "system_stats", "claude_stats",
             "git_stats", "telemetry", "ld_tasks", "tokscale_stats")
    kwargs = {name: feed for name in names}
    result = emit.render(([week], [], []), [], tmp_path, {"schedule": private},
                         datetime(2026, 8, 1, tzinfo=timezone.utc), "", "", **kwargs)
    for page in (result, tmp_path / "settings.html"):
        content = page.read_text(encoding="utf-8")
        assert "/home/" not in content
        assert "fixtureuser" not in content.lower()
        assert "fixturehost" not in content.lower()
    content = result.read_text(encoding="utf-8")
    assert "~/code/project" in content
    assert "relative/src.py" in content
    payload = content.split("window.__WEEKLY__ = ", 1)[1].split(";</script>", 1)[0]
    assert json.loads(payload)["projects_stats"]

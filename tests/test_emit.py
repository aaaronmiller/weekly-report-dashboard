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

from datetime import datetime, timezone

from scripts.capacity import load_capacity
from scripts.emit import render


def test_capacity_render_and_unavailable(tmp_path):
    data = {
        'schema_version': 1, 'generated_at': '2026-11-16T12:00:00Z',
        'pools': [{'name': 'codex', 'observed_at': '2026-11-16T11:00:00Z', 'stale': True,
                   'windows': {'weekly': {'used_fraction': .4, 'remaining_hours': 3,
                                           'projected_fraction': 1.2, 'pace_score': 6, 'mode': 'burn'},
                               'five_hour': {'used_fraction': .1, 'pace_score': 3, 'mode': 'stretch'}}}],
        'efficiency': {'by_tier': {}, 'reason': 'no dispatched attempts yet'},
        'concurrency': {'processes': {'codex': 2}, 'active_claude_subagent_transcripts': 1},
        'meta_analysis': {'trend': {'runs': 2, 'falling': True},
                          'series': [{'date': '2026-11-16', 'trigger': 'nightly', 'items_observed': 4,
                                      'items_fixed': 2, 'next_run': '2026-11-17', 'notes': 'PRIVATE_PROMPT'}]},
        'argv': ['PRIVATE_ARGV'],
    }
    args = (([], [], []), [], tmp_path, {}, datetime(2026, 11, 16, tzinfo=timezone.utc), '', '')
    page = render(*args, capacity=data).read_text()
    for value in ('Capacity and pace', '40.0%', 'projects 120.0% at reset', '6.0/10', 'hits cap early',
                  'Burn', 'will waste', 'Stretch', 'stale', 'no dispatched attempts yet',
                  'codex: 2', 'trend: falling', '2026-11-17'):
        assert value in page
    assert 'PRIVATE_PROMPT' not in page and 'PRIVATE_ARGV' not in page
    assert 'Telemetry unavailable.' in render(*args, capacity=load_capacity(tmp_path / 'missing')).read_text()
    (tmp_path / 'invalid.json').write_text('{')
    assert load_capacity(tmp_path / 'invalid.json') is None

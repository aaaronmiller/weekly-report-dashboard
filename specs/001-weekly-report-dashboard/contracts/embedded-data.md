# Contract: Embedded Data Payload

The generator emits exactly one JSON literal into the page. The browser treats
it as read-only; every view is a projection over it.

```js
window.__WEEKLY__ = {
  schema_version: 1,
  generated_at: "2026-08-01T00:00:00Z",   // derived from newest input mtime
  config: {
    dark_work_threshold: 8.0,
    stall_age: 3
  },
  weeks: [ /* WeekRecord */ ],
  carry_over: [ /* CarryOverItem */ ],
  project_activity: [ /* ProjectWeekActivity */ ],
  assertions: [ /* ValidationAssertion */ ],
  coverage: {
    weeks_total: 12,
    with_pair: 12,
    with_bundle: 6,
    with_both: 6,
    missing: 7
  }
}
```

## Rules

1. **Single source.** No figure may hold its own copy of any value. Every chart
   series is computed from `weeks`, `carry_over`, or `project_activity` at
   render time. This is Constitution Principle I expressed as a data contract.

2. **Nulls survive serialization.** A missing value serializes as JSON `null`,
   never `0` and never omitted. Consumers must distinguish `null` from `0`.

3. **No mutation.** The page must not write to `window.__WEEKLY__`. Derived
   values are computed into local scope.

4. **Assertions are data.** The page reads `assertions` and renders a failure
   banner when any `passed` is false. The page does not re-derive assertions.

5. **Ordering is stable.** `weeks` is sorted ascending by `week_ending`;
   `carry_over` is sorted descending by `carry_age` then by `normalized_text`.
   Stable ordering is required for byte-identical output.

## Serialization

`json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)`

Dates serialize as ISO-8601 strings. `sort_keys` and fixed separators are
required by SC-005.

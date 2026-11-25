# Testing Documentation

## Strategy

Tests assert observable behavior, not internal implementation. Each test runs the real pipeline over the simulated feed and checks the resulting log, alert, index query, or agent answer. The suite uses pytest and standard-library assertions. No network, model, or GPU is involved.

Run the suite from the repository root.

```powershell
uv sync
uv run pytest -q
```

## Test cases

| # | Name | Input | Expected result |
| --- | --- | --- | --- |
| 1 | Truck logged correctly | Frame described as `Blue Ford F150 at garage, 12:00` | An event exists with make `Ford`, model `F150`, color `blue`, location `garage`, time `12:00` |
| 2 | Alert triggered at midnight | Frame described as `Person loitering at main gate, 00:01` | A high severity alert with message `Person loitering at main gate, 00:01.` |
| 3 | Repeat entry alert | Full sample feed | A medium severity alert says the F150 entered twice today at `00:05` and `12:00` |
| 4 | Query by object | Full sample feed | Querying vehicle make `Ford` and model `F150` returns both sightings |
| 5 | Query by time range | Full sample feed | Querying `00:00` to `06:00` returns the first three frames |
| 6 | Agent follow-up question | Question `What objects were in the video?` after running the feed | Answer names the Ford F150, the person, and the delivery van |
| 7 | Agent vehicle question | Question `When was the blue Ford F150 seen?` | Answer includes `00:05` and `12:00` |
| 8 | Agent truck question | Question `Show all truck events` | Answer includes both F150 events and no van or person events |
| 9 | Summary | `summarize()` after running the feed | A single non-empty sentence naming the detections and alerts |

## Dynamic input scenarios

The feed is deterministic so tests are repeatable. To exercise dynamic input, pass any list of `Frame` objects to `SecurityAnalystPipeline.run(frames)`. The analyzer reads the `description` field, so changing a description changes the detection without changing code.

Examples worth running by hand.

- Change the gate time from `00:01` to `02:30`. The loitering rule still fires because the time is inside the 00:00 to 05:00 window.
- Change the gate time to `09:00`. The loitering rule does not fire.
- Add a third F150 sighting. The repeat entry rule still fires once and the object query returns three rows.
- Remove all person frames. The loitering rule emits nothing and the other rules still produce output.

## Emergency response scenarios

The two rules model the emergency paths in the spec.

1. **After-hours loitering.** A person at the main gate before 05:00 produces a high severity alert immediately after that frame is processed. The alert carries the frame id so an operator can jump to the source.
2. **Repeated entry.** A vehicle seen a second time produces a medium severity alert naming the make and model. This covers the "entered twice today" example.

Both alerts are returned in the pipeline result and printed by the demo. They are derived from stored events, so the index and the alert output cannot disagree.

## Validation result

All nine cases pass with `uv run pytest -q`. The demo command `uv run drone-analyst` completes and prints logs, alerts, indexed query results, agent answers, and a summary. The observed run produced 6 frames, 5 events, and 2 alerts. Exact command output is captured in the demo screen recording referenced by the report.

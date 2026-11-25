# Feature Spec: Drone Security Analyst Agent

## Value to property owners

A docked drone can watch a fixed property every day, but raw footage is useless unless someone reviews it. This agent turns each video frame and telemetry sample into a short, searchable record and raises an immediate alert when a rule is broken. A property owner gets a written log of what happened, can ask what was seen, and is told about suspicious activity without watching hours of video.

## Key requirements

1. **Ingest and log.** Accept simulated telemetry and text-described frames in chronological order. Produce a record for each detected object with its time, location, and attributes such as color, make, and model.
2. **Index and retrieve.** Store frames and events in a queryable index. Answer questions such as "show all truck events" and "what happened between 00:00 and 01:00".
3. **Alert in real time.** Evaluate every new event against a small set of security rules. Emit an immediate alert for after-hours loitering at the main gate and for a vehicle that enters the property twice in one day.

## Scope and exclusions

The prototype uses text descriptions as simulated video frames. The assignment explicitly allows this. The system does not perform real visual inference, does not use LangChain, and does not require a GPU or network access. It is built with the Python standard library and pytest. These choices are deliberate and are explained in `docs/REPORT.md`.

## Success criteria

- A blue Ford F150 seen at two locations is logged twice and flagged as a repeat entry.
- A person at the main gate at 00:01 produces a high severity loitering alert.
- The index returns the correct frames and events when queried by object or by time range.
- The agent can answer a follow-up question and produce a one-sentence summary.
- All pytest tests pass and the demo runs from a clean checkout with `uv`.

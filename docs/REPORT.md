# Drone Security Analyst Agent

## AI Engineer Assignment Report

### 1. Executive summary

This prototype is a Drone Security Analyst Agent for a docked drone that watches a fixed property. It reads simulated telemetry and text-described video frames, turns each frame into structured detections, stores them in a queryable index, raises alerts from a small rule registry, and answers questions about the recording. The build uses Python and the standard library, is packaged with uv, and passes a pytest suite that checks the behaviors named in the assignment.

The central design choice is to treat frames as text descriptions rather than images. The assignment explicitly allows this, and it let the whole system stay local, deterministic, and testable. The same choice also made it possible to finish without prior VLM or LangChain knowledge, which is discussed openly in section 9.

### 2. Goal and feature spec

The value to a property owner is continuous oversight without manual footage review. The agent produces a written log of what was seen, keeps it searchable, and raises an immediate alert when a security rule is broken.

Three requirements drove the build.

1. Ingest telemetry and frames and log each detection with time, location, and object attributes.
2. Store frames and events so they can be queried by time range or by object.
3. Emit real-time alerts for after-hours loitering at the main gate and repeated vehicle entry.

The full spec is in `docs/SPEC.md`.

### 3. Assumptions

- **Frame representation.** A frame is a short text description such as `Frame 3: Person loitering at main gate`. The assignment names this as an acceptable simulation of video frames.
- **Telemetry representation.** Telemetry is a timestamp, a location label, a two-dimensional position, and an altitude in metres. It is attached to each frame.
- **Objects of interest.** The domain is deliberately small: people and vehicles, with color, make, and model as attributes. This is enough to express the required examples.
- **Single property and single day.** The feed covers one day at one property. The design does not attempt multi-site federation.
- **Rule-based alerts.** "Security rules" are interpreted as explicit, deterministic conditions rather than a learned model. This makes alerts explainable and testable.
- **AI assistance.** AI-assisted coding tools are permitted and expected by the assignment. Their use is documented in section 8.

### 4. Approach and architecture

The system is a one-directional pipeline of six stages.

1. **Feed** produces frames and telemetry in timestamp order.
2. **Analyzer** parses each frame description into a list of typed entities.
3. **Indexer** writes frames and detections to SQLite with indices on time and object fields.
4. **Alert engine** evaluates each new event against a registry of rules.
5. **Agent** holds rolling context, answers follow-up questions, and produces a one-sentence summary.
6. **Entry point** prints the logs, alerts, query results, answers, and summary.

The data model is a set of typed values: `Telemetry`, `Entity`, `Frame`, `SecurityEvent`, and `Alert`. Encoding the domain this way keeps the shape consistent across stages and removes repeated checks. The alert rules are a registry of objects sharing one `evaluate` signature, so a new rule is one new entry rather than a new branch in a shared function. The index is the single source of truth for queries, and the agent reads from it instead of keeping a second copy.

A Mermaid diagram is in `diagrams/architecture.mmd` and the same flow is described in `docs/ARCHITECTURE.md`.

### 5. Implementation details

The package lives under `src/drone_analyst/`.

- `models.py` defines the five dataclasses.
- `feed.py` builds the sample day, including a blue Ford F150 at the garage at 12:00, the same vehicle at the main gate at 00:05, and a person at the main gate at 00:01.
- `analyzer.py` maps keywords in the description to entities. This is the AI-generated component that was reviewed and customized; it stands in for a VLM in this prototype.
- `indexer.py` owns the SQLite schema and the `query_by_time` and `query_by_object` methods.
- `alerts.py` holds the rule registry. The loitering rule fires for a person at the main gate between 00:00 and 05:00. The repeat entry rule fires when a make and model appear at two distinct times.
- `agent.py` answers questions and summarizes.
- `pipeline.py` wires the stages. `main.py` is the demo.

### 6. Choice of tools and justification

**Text frames instead of a real VLM (CLIP or BLIP).** A VLM would need model weights, a download step, and GPU or CPU inference time. Text-described frames are explicitly allowed by the assignment and let the analyzer be inspected and tested directly. The tradeoff is that the analyzer only understands its keyword set. A real VLM would generalize to unseen images. The interface `analyze_frame(frame)` is kept small so a VLM can be dropped in later without changing the rest of the pipeline.

**Plain Python instead of LangChain.** LangChain is useful for chaining LLM calls, managing prompts, and tool use. None of those are needed here, because the agent behavior is a few deterministic methods over stored events. Adding it would add a dependency and a learning cost with no improvement in correctness. The agent module keeps the same conceptual role that a LangChain agent would play, so the migration path is clear.

**SQLite instead of a JSON file or pandas.** SQLite is in the standard library, supports indexed queries, and persists with a file path. A JSON file would require loading the whole log for every query. pandas would add a dependency for a small dataset.

**Rule registry instead of conditionals.** Rules are independent and grow over time. A registry keeps each rule in one place and lets the engine stay unchanged as rules are added.

**uv for packaging.** uv resolves and locks the environment quickly and gives a single command for tests and the demo. There are no runtime dependencies, which keeps a clean checkout easy to run.

### 7. Results

The demo produces the following kinds of output.

- **Log.** `Blue Ford F150 spotted at garage, 12:00.`
- **Alert.** `Person loitering at main gate, 00:01.`
- **Second alert.** `Blue Ford F150 entered twice today (00:05, 12:00).`
- **Indexed query.** Asking for all Ford F150 events returns the 00:05 gate sighting and the 12:00 garage sighting.
- **Agent answer.** A question about the vehicle returns both times, demonstrating that context is used across the recording.
- **Summary.** One sentence covering the vehicles and the person seen during the day.

These outputs come from the same stored events, so the log, the alert, and the query result cannot disagree. Ten automated cases verify the behaviors. The observed run processed 6 frames, logged 5 events, and raised 2 alerts. A load run indexed 1000 frames and 1000 events in 0.02s and returned 500 rows from a vehicle query. Full cases and results are in `docs/TESTING.md`.

### 8. How AI tools assisted

AI-assisted coding through OpenCode was used at every stage. It drafted the frame analyzer, the alert rule registry, the pytest suite, and the documentation. It also helped validate the architecture by restating the pipeline and pointing out where state could be duplicated between the index and the agent. The first drafts were reviewed rather than accepted directly. The data shape was fixed before code was written, the parser keywords and rule thresholds were corrected against the spec, and the test assertions were checked by running the suite. The main value was speed on boilerplate and a first test matrix. The main risk was plausible-looking code that did not match the requirement, which review and tests were used to catch.

### 9. Note on experience and learning approach

The author has no prior knowledge of VLMs or LangChain. The assignment asks novices to say so and states that effort and learning approach will be considered. The learning path was to read the problem, choose the text-frame simulation the assignment permits, reduce the agent to its essential behavior, and use AI assistance to understand and draft each component. The result is a working system that covers the required behaviors and exposes a clean seam where a real VLM or an agent framework could be introduced later.

### 10. Limitations

- The analyzer matches keywords and cannot interpret images or unseen phrasing.
- Rules are fixed and time-based. They do not learn from past days.
- The index targets one property and one day of frames.
- No real video, audio, or telemetry hardware is involved.

### 11. What could be done with more time

- Replace the text analyzer with a real VLM behind the same interface and compare its descriptions against the keyword baseline.
- Add video summarization beyond the current one-sentence summary, such as a per-hour activity digest.
- Add a proper LangChain agent with tool calling so questions can trigger new index queries automatically.
- Add anomaly detection on telemetry, such as an unexpected altitude change, as an additional rule.
- Support multiple properties and long recordings with a file-backed or columnar store and batched inserts.
- Record and attach the required demo videos with voiceover. The screen recording is a manual deliverable and is referenced in section 12.

### 12. Videos

Demo screen recordings are to be attached by the candidate. They should show frame descriptions, the analyzer output, the generated alerts, the context summary, the agent recommendations, an indexed query, and a scalability example. Each video must include voiceover, as the assignment states that videos without voiceover lead to incorrect analysis.

### 13. Conclusion

The prototype meets the functional requirements of the assignment. It logs detections, indexes them for retrieval, alerts on the two named security conditions, and uses context across the recording to answer questions. It is small, dependency-light, and verified by tests. The design leaves explicit seams for a real VLM and an agent framework once the time budget allows.

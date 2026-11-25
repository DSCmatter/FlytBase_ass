# Drone Security Analyst Agent

A minimal prototype for the FlytBase AI Engineer assignment. It processes simulated drone telemetry and text-described video frames, indexes every observation, raises rule-based security alerts, and answers questions about what was seen.

> **Note on experience.** The author has no prior knowledge of VLMs or LangChain. The assignment permits simulated frames described in text, so the prototype uses a small deterministic parser in place of a VLM and plain Python classes in place of LangChain. This is stated openly in the report. The learning path is documented there as well.

## Quick start

Requires Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```powershell
uv sync
uv run pytest -q
uv run drone-analyst
```

`uv sync` creates the environment from `pyproject.toml`. The project has no runtime dependencies beyond the standard library. `pytest` is a development dependency.

Alternative entry point:

```powershell
uv run python -m drone_analyst.main
```

To regenerate the PDF report from `docs/REPORT.md`:

```powershell
uv run --with reportlab python tools/make_report.py
```

## What the demo shows

Running `uv run drone-analyst` prints five sections.

1. **Logs**, one line per detected object, for example `Blue Ford F150 spotted at garage, 12:00.`
2. **Alerts**, for example `Person loitering at main gate, 00:01.`
3. **Indexed frames**, queryable by object and by time range.
4. **Agent answers**, including a follow-up question about the vehicle.
5. **Summary**, a single sentence describing the recording.

## Project layout

```text
src/drone_analyst/
    models.py      typed domain values
    feed.py        deterministic simulated frames and telemetry
    analyzer.py    frame text to structured entities
    indexer.py     SQLite storage and queries
    alerts.py      rule registry
    agent.py       context, follow-up questions, summary
    pipeline.py    stage wiring
    main.py        demo output
tests/
    test_pipeline.py
docs/
    SPEC.md             feature spec
    REPORT.md           source for the PDF report
    report.pdf          submitted PDF report
    TESTING.md          test cases and results
    ARCHITECTURE.md     design and decisions
diagrams/               architecture diagram
```

## Design decisions

The pipeline is one directional flow of typed values. A registry holds the alert rules. SQLite is the single queryable source of truth. There is no hidden state duplicated between the index and the agent. Full reasoning and an alternatives table are in `docs/ARCHITECTURE.md`.

## How AI tools were used

AI-assisted coding through OpenCode was used throughout this build. It drafted the frame analyzer, the alert rule registry, the pytest cases, and the documentation. Each draft was reviewed and constrained by the data model described above. The parser keywords, the rule thresholds, and the test assertions were adjusted during review so that behavior matched the spec rather than the first generated version. The AI tool reduced boilerplate and produced the first test matrix, which was then checked by running the suite.

## Limitations

- Frames are text descriptions, not real images. The analyzer matches keywords and cannot handle unseen phrasing.
- Rules are fixed and time-based. They do not learn from history.
- The index is local SQLite meant for one property and one day of frames.

## Submission contents

- Source code and tests under `src/` and `tests/`
- This README, `docs/ARCHITECTURE.md`, `docs/SPEC.md`, `docs/TESTING.md`
- `docs/report.pdf` and its source `docs/REPORT.md`
- Architecture diagram under `diagrams/`
- Demo screen recording with voiceover, to be attached by the candidate

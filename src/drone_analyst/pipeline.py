from collections import defaultdict
from dataclasses import dataclass

from .agent import AnalystAgent
from .alerts import evaluate_all
from .analyzer import analyze_frame
from .indexer import FrameIndexer
from .models import Alert, Frame, SecurityEvent, clock


@dataclass
class PipelineResult:
    frames: list[Frame]
    events: list[SecurityEvent]
    alerts: list[Alert]
    agent: AnalystAgent


class SecurityAnalystPipeline:
    def __init__(self, indexer: FrameIndexer | None = None):
        self.indexer = indexer or FrameIndexer()
        self.agent = AnalystAgent()

    def run(self, frames: list[Frame]) -> PipelineResult:
        self.agent = AnalystAgent()
        events: list[SecurityEvent] = []
        for frame in frames:
            analyze_frame(frame)
            self.indexer.insert_frame(frame)
            for entity in frame.entities:
                event = SecurityEvent(
                    event_id=len(events) + 1,
                    frame_id=frame.id,
                    timestamp=frame.timestamp,
                    location=frame.location,
                    entity=entity,
                    summary=f"{entity.label} spotted at {frame.location}, {clock(frame.timestamp)}.",
                )
                events.append(event)
                self.indexer.insert_event(event)

        alerts = evaluate_all(events, frames, {})
        alerts_by_frame: dict[int, list[Alert]] = defaultdict(list)
        for alert in alerts:
            alerts_by_frame[alert.frame_id].append(alert)
        frames_by_id = {frame.id: frame for frame in frames}
        for event in events:
            self.agent.observe(
                frames_by_id[event.frame_id],
                event,
                alerts_by_frame[event.frame_id],
            )

        return PipelineResult(frames=frames, events=events, alerts=alerts, agent=self.agent)

    def query_by_time(self, start: str, end: str) -> list[dict]:
        return self.indexer.query_by_time(start, end)

    def query_by_object(
        self,
        kind: str | None = None,
        make: str | None = None,
        model: str | None = None,
    ) -> list[dict]:
        return self.indexer.query_by_object(kind=kind, make=make, model=model)

    def ask(self, question: str) -> str:
        return self.agent.ask(question)

    def close(self) -> None:
        self.indexer.close()

from collections import defaultdict
from dataclasses import replace
from datetime import datetime

from .models import Alert, Frame, SecurityEvent, clock


class LoiteringRule:
    name = "loitering"

    def evaluate(
        self,
        events: list[SecurityEvent],
        frames: list[Frame],
        context: dict,
    ) -> list[Alert]:
        start_hour, end_hour = context.get("quiet_hours", (0, 5))
        alerts: list[Alert] = []
        for event in events:
            if event.entity.kind != "person" or event.location.lower() != "main gate":
                continue
            if not start_hour <= datetime.fromisoformat(event.timestamp).hour < end_hour:
                continue
            alerts.append(
                Alert(
                    rule=self.name,
                    severity="high",
                    message=f"Person loitering at main gate, {clock(event.timestamp)}.",
                    timestamp=event.timestamp,
                    frame_id=event.frame_id,
                )
            )
        return alerts


class RepeatEntryRule:
    name = "repeat-entry"

    def evaluate(
        self,
        events: list[SecurityEvent],
        frames: list[Frame],
        context: dict,
    ) -> list[Alert]:
        min_sightings = context.get("min_sightings", 2)
        sightings: dict[tuple[str, str], list[SecurityEvent]] = defaultdict(list)
        for event in events:
            if event.entity.kind == "vehicle" and event.entity.model:
                sightings[(event.entity.make, event.entity.model)].append(event)

        alerts: list[Alert] = []
        for group in sightings.values():
            times = sorted({event.timestamp for event in group})
            if len(times) < min_sightings:
                continue
            latest = max(group, key=lambda event: event.timestamp)
            occurrences = "twice" if len(times) == 2 else f"{len(times)} times"
            seen_at = ", ".join(clock(timestamp) for timestamp in times)
            alerts.append(
                Alert(
                    rule=self.name,
                    severity="medium",
                    message=f"{latest.entity.label} entered {occurrences} today ({seen_at}).",
                    timestamp=latest.timestamp,
                    frame_id=latest.frame_id,
                )
            )
        return alerts


REGISTRY = [LoiteringRule(), RepeatEntryRule()]


def evaluate_all(
    events: list[SecurityEvent],
    frames: list[Frame],
    context: dict | None = None,
) -> list[Alert]:
    context = context or {}
    alerts: list[Alert] = []
    for rule in REGISTRY:
        alerts.extend(rule.evaluate(events, frames, context))
    return [replace(alert, alert_id=index) for index, alert in enumerate(alerts, 1)]

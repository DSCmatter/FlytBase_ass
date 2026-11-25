from collections import deque

from .analyzer import VEHICLE_CATEGORIES, parse_entities
from .models import Alert, Entity, Frame, SecurityEvent, clock


def _join(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


class AnalystAgent:
    def __init__(self, history: int = 100):
        self.events: deque[SecurityEvent] = deque(maxlen=history)
        self.alerts: list[Alert] = []
        self._alert_ids: set[int] = set()

    def observe(self, frame: Frame, event: SecurityEvent, alerts: list[Alert]) -> None:
        self.events.append(event)
        for alert in alerts:
            if alert.alert_id not in self._alert_ids:
                self._alert_ids.add(alert.alert_id)
                self.alerts.append(alert)

    def ask(self, question: str) -> str:
        text = question.lower()
        if "what objects" in text or "which objects" in text:
            return self._objects_answer()
        if "when" in text:
            return self._when_answer(text)
        if "show" in text or "events" in text:
            return self._events_answer(text)
        return "Ask me what objects were seen, to show events, or when an object was seen."

    def summarize(self) -> str:
        if not self.events:
            return "No security events were observed."

        events = list(self.events)
        vehicles = sum(1 for event in events if event.entity.kind == "vehicle")
        people = sum(1 for event in events if event.entity.kind == "person")
        details = []
        if vehicles:
            details.append(f"{vehicles} vehicle sightings")
        if people:
            details.append(f"{people} person sightings")

        sentence = f"The drone logged {len(events)} events over the day"
        if details:
            sentence += ", including " + " and ".join(details)

        alerts = self.alerts
        if alerts:
            high = sum(1 for alert in alerts if alert.severity == "high")
            lead = next((alert for alert in alerts if alert.severity == "high"), alerts[0])
            sentence += (
                f", and raised {len(alerts)} alerts ({high} high), "
                f"led by {lead.message.rstrip('.').lower()}"
            )
        return sentence + "."

    def _objects_answer(self) -> str:
        labels = list(dict.fromkeys(event.entity.label for event in self.events))
        if not labels:
            return "No objects were seen."
        return "Objects seen: " + ", ".join(labels) + "."

    def _when_answer(self, text: str) -> str:
        query = self._detected_entity(text)
        if query is None:
            return "I could not match that object to anything in the video."

        matches = [event for event in self.events if self._matches(event.entity, query)]
        if not matches:
            return f"I did not see a {query.label.lower()} in the video."

        label = matches[0].entity.label
        times = list(dict.fromkeys(clock(event.timestamp) for event in matches))
        return f"The {label[0].lower() + label[1:]} was seen at {_join(times)}."

    def _events_answer(self, text: str) -> str:
        query = self._detected_entity(text)
        events = list(self.events)
        if query is not None:
            events = [event for event in events if self._matches(event.entity, query)]

        if not events:
            return "No matching events were logged."

        parts = [
            f"{event.entity.label} at {event.location}, {clock(event.timestamp)}"
            for event in events
        ]
        return "Events: " + "; ".join(parts) + "."

    @staticmethod
    def _detected_entity(text: str) -> Entity | None:
        entities = parse_entities(text)
        return entities[0] if entities else None

    @staticmethod
    def _matches(candidate: Entity, query: Entity) -> bool:
        if candidate.kind != query.kind:
            return False
        if query.color and candidate.color != query.color:
            return False
        if query.make and candidate.make.lower() != query.make.lower():
            return False
        if query.model:
            models = VEHICLE_CATEGORIES.get(query.model.lower(), (query.model,))
            if candidate.model not in models:
                return False
        return True

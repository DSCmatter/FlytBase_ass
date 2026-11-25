from dataclasses import dataclass, field


@dataclass(frozen=True)
class Telemetry:
    timestamp: str
    location: str
    position: tuple[float, float]
    altitude_m: float


@dataclass(frozen=True)
class Entity:
    kind: str
    color: str
    make: str
    model: str
    count: int = 1

    @property
    def label(self) -> str:
        parts = (self.color.title(), self.make, self.model)
        return " ".join(part for part in parts if part) or self.kind.title()


@dataclass
class Frame:
    id: int
    timestamp: str
    location: str
    description: str
    telemetry: Telemetry
    entities: list[Entity] = field(default_factory=list)


@dataclass(frozen=True)
class SecurityEvent:
    event_id: int
    frame_id: int
    timestamp: str
    location: str
    entity: Entity
    summary: str


@dataclass(frozen=True)
class Alert:
    rule: str
    severity: str
    message: str
    timestamp: str
    frame_id: int
    alert_id: int = 0


def clock(timestamp: str) -> str:
    """Return HH:MM from an ISO timestamp."""
    return timestamp[11:16]

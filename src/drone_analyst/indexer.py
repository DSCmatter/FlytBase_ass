import sqlite3
from pathlib import Path

from .models import Frame, SecurityEvent

SCHEMA = """
CREATE TABLE IF NOT EXISTS frames (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    position_x REAL NOT NULL,
    position_y REAL NOT NULL,
    altitude_m REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY,
    frame_id INTEGER NOT NULL REFERENCES frames(id),
    timestamp TEXT NOT NULL,
    location TEXT NOT NULL,
    kind TEXT NOT NULL,
    color TEXT NOT NULL,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    count INTEGER NOT NULL,
    summary TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_frames_timestamp ON frames(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_kind ON events(kind);
CREATE INDEX IF NOT EXISTS idx_events_make_model ON events(make, model);
"""


class FrameIndexer:
    def __init__(self, path: str | Path = ":memory:"):
        self._conn = sqlite3.connect(str(path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    def insert_frame(self, frame: Frame) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO frames
                (id, timestamp, location, description, position_x, position_y, altitude_m)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                frame.id,
                frame.timestamp,
                frame.location,
                frame.description,
                frame.telemetry.position[0],
                frame.telemetry.position[1],
                frame.telemetry.altitude_m,
            ),
        )
        self._conn.commit()

    def insert_event(self, event: SecurityEvent) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO events
                (event_id, frame_id, timestamp, location, kind, color, make, model, count, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.frame_id,
                event.timestamp,
                event.location,
                event.entity.kind,
                event.entity.color,
                event.entity.make,
                event.entity.model,
                event.entity.count,
                event.summary,
            ),
        )
        self._conn.commit()

    def query_by_time(self, start: str, end: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM frames WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp",
            (start, end),
        ).fetchall()
        return [dict(row) for row in rows]

    def query_by_object(
        self,
        kind: str | None = None,
        make: str | None = None,
        model: str | None = None,
    ) -> list[dict]:
        conditions: list[str] = []
        params: list[str] = []
        if kind is not None:
            conditions.append("kind = ?")
            params.append(kind)
        if make is not None:
            conditions.append("make = ?")
            params.append(make)
        if model is not None:
            conditions.append("model = ?")
            params.append(model)

        query = "SELECT * FROM events"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY timestamp"

        rows = self._conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self._conn.close()

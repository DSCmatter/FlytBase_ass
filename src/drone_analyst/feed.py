from .models import Frame, Telemetry

DATE = "2026-11-25"


def _frame(
    frame_id: int,
    time: str,
    location: str,
    description: str,
    position: tuple[float, float],
    altitude_m: float,
) -> Frame:
    timestamp = f"{DATE}T{time}:00"
    return Frame(
        id=frame_id,
        timestamp=timestamp,
        location=location,
        description=description,
        telemetry=Telemetry(
            timestamp=timestamp,
            location=location,
            position=position,
            altitude_m=altitude_m,
        ),
    )


def build_sample_frames() -> list[Frame]:
    return [
        _frame(1, "00:01", "main gate", "Frame 1: Person loitering at main gate", (12.0, 4.0), 42.0),
        _frame(2, "00:05", "main gate", "Frame 2: Blue Ford F150 at main gate", (12.5, 5.0), 45.0),
        _frame(3, "03:00", "main gate", "Frame 3: Empty main gate, no activity", (11.0, 3.0), 60.0),
        _frame(4, "09:00", "loading dock", "Frame 4: White delivery van at loading dock", (30.0, 10.0), 38.0),
        _frame(5, "12:00", "garage", "Frame 5: Blue Ford F150 at garage", (18.0, 22.0), 50.0),
        _frame(6, "18:30", "driveway", "Frame 6: Person walking on driveway", (25.0, 8.0), 33.0),
    ]

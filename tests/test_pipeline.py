import pytest

from drone_analyst.feed import build_load_frames, build_sample_frames
from drone_analyst.pipeline import SecurityAnalystPipeline


@pytest.fixture
def pipeline():
    pipe = SecurityAnalystPipeline()
    try:
        yield pipe
    finally:
        pipe.close()


@pytest.fixture
def result(pipeline):
    return pipeline.run(build_sample_frames())


def test_f150_logged_with_telemetry_context(result):
    events = [
        event
        for event in result.events
        if event.entity.model == "F150" and event.location == "garage"
    ]
    assert len(events) == 1

    event = events[0]
    assert event.entity.make == "Ford"
    assert event.entity.color == "blue"
    assert event.timestamp == "2026-11-25T12:00:00"
    assert event.summary == "Blue Ford F150 spotted at garage, 12:00."


def test_loitering_alert_at_midnight(result):
    alerts = [alert for alert in result.alerts if alert.rule == "loitering"]
    assert len(alerts) == 1

    alert = alerts[0]
    assert alert.severity == "high"
    assert alert.message == "Person loitering at main gate, 00:01."
    assert alert.frame_id == 1


def test_repeat_entry_alert_for_f150(result):
    alerts = [alert for alert in result.alerts if alert.rule == "repeat-entry"]
    assert len(alerts) == 1

    alert = alerts[0]
    assert alert.severity == "medium"
    assert "F150" in alert.message
    assert "twice today" in alert.message


def test_index_query_by_object_returns_all_f150_events(pipeline, result):
    rows = pipeline.query_by_object(make="Ford", model="F150")

    assert [row["timestamp"] for row in rows] == [
        "2026-11-25T00:05:00",
        "2026-11-25T12:00:00",
    ]
    assert {row["location"] for row in rows} == {"main gate", "garage"}


def test_index_query_by_time_range(pipeline, result):
    rows = pipeline.query_by_time("2026-11-25T00:00:00", "2026-11-25T06:00:00")

    assert [row["id"] for row in rows] == [1, 2, 3]


def test_agent_answers_when_vehicle_was_seen(result):
    answer = result.agent.ask("When was the blue Ford F150 seen?")

    assert "F150" in answer
    assert "00:05" in answer
    assert "12:00" in answer


def test_agent_lists_objects_seen(result):
    answer = result.agent.ask("What objects were in the video?")

    assert "Person" in answer
    assert "F150" in answer
    assert "Delivery Van" in answer


def test_agent_shows_truck_events(result):
    answer = result.agent.ask("Show all truck events")

    assert "F150" in answer
    assert "Delivery Van" not in answer
    assert "Person" not in answer


def test_agent_summary_is_one_sentence(result):
    summary = result.agent.summarize()

    assert summary.endswith(".")
    assert "\n" not in summary
    assert "alert" in summary.lower()


def test_load_frames_have_unique_ids_and_timestamps():
    frames = build_load_frames(120)

    assert len({frame.id for frame in frames}) == 120
    assert len({frame.timestamp for frame in frames}) == 120

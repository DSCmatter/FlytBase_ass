from time import perf_counter

from .feed import build_load_frames, build_sample_frames
from .models import clock
from .pipeline import SecurityAnalystPipeline

QUESTIONS = (
    "What objects were in the video?",
    "Show all truck events",
    "When was the blue Ford F150 seen?",
)


def main() -> None:
    frames = build_sample_frames()
    pipeline = SecurityAnalystPipeline()
    try:
        result = pipeline.run(frames)
        day = frames[0].timestamp[:10]
        start = f"{day}T00:00:00"
        end = f"{day}T06:00:00"

        print("Drone Security Analyst demo")
        print(
            f"Processed {len(result.frames)} frames, logged {len(result.events)} events, "
            f"raised {len(result.alerts)} alerts."
        )

        print("\nLogs")
        for event in result.events:
            print(f"  {clock(event.timestamp)}  {event.location:<12} {event.summary}")

        print("\nAlerts")
        for alert in result.alerts:
            print(f"  [{alert.severity}] {alert.rule}: {alert.message}")

        print(f"\nIndexed frames {clock(start)}-{clock(end)}")
        for row in pipeline.query_by_time(start, end):
            print(f"  #{row['id']} {clock(row['timestamp'])} {row['location']}: {row['description']}")

        print("\nIndexed Ford F150 events")
        for row in pipeline.query_by_object(make="Ford", model="F150"):
            print(f"  {clock(row['timestamp'])} {row['location']}: {row['summary']}")

        print("\nAgent answers")
        for question in QUESTIONS:
            print(f"  Q: {question}")
            print(f"  A: {result.agent.ask(question)}")

        print("\nSummary")
        print(f"  {result.agent.summarize()}")

        print("\nScalability")
        load_pipeline = SecurityAnalystPipeline()
        try:
            started = perf_counter()
            load_result = load_pipeline.run(build_load_frames())
            elapsed = perf_counter() - started
            vehicle_rows = load_pipeline.query_by_object(kind="vehicle")
            print(
                f"  Indexed {len(load_result.frames)} frames and {len(load_result.events)} "
                f"events in {elapsed:.2f}s."
            )
            print(f"  Vehicle query returned {len(vehicle_rows)} rows.")
        finally:
            load_pipeline.close()
    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
